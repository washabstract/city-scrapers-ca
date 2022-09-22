import re
from datetime import datetime

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider, LegistarSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class SanDiegoCountyLegSpider(LegistarSpider):
    name = "san_diego_county_leg"
    agency = "County of San Diego"
    timezone = "America/Los_Angeles"
    start_urls = ["https://sdcounty.legistar.com/Calendar.aspx"]
    link_types = []

    def parse_legistar(self, events):
        for event in events:
            meeting = Meeting(
                title=event["Name"].title(),
                description=self._parse_description(event),
                classification=self._parse_classification(event),
                start=self.legistar_start(event),
                end=self._parse_end(event),
                all_day=self._parse_all_day(event),
                time_notes=self._parse_time_notes(event),
                location=self._parse_location(event),
                links=self.legistar_links(event),
                source=self.legistar_source(event),
                created=datetime.now(),
                updated=datetime.now(),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def legistar_start(self, item):
        start_date = item.get("Meeting Date")
        start_time = item.get("Meeting Time")
        if start_date and start_time:
            try:
                return datetime.strptime(
                    f"{start_date} {start_time}", "%m/%d/%Y %I:%M %p"
                )
            except ValueError:
                return datetime.strptime(start_date, "%m/%d/%Y")
        if start_date:
            try:
                return datetime.strptime(start_date, "%m/%d/%Y")
            except ValueError:
                return None  # this will cause an error down the line anyway, so idk

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item):
        title = item["Name"].title()
        for classification in CLASSIFICATIONS:
            if classification in title:
                return classification
        return NOT_CLASSIFIED

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        location = item["Meeting Location"]
        if type(location) is dict:
            return {
                "address": location.get("url", ""),
                "name": location.get("label", ""),
            }
        clean_location = re.sub("\r\n", " ", location)
        clean_location = re.sub("\xa0", " ", clean_location)
        return {
            "address": "1600 Pacific Highway, San Diego, CA 92101",
            "name": clean_location,
        }


class SanDiegoCountySpider(CityScrapersSpider):
    name = "san_diego_county"
    agency = "County of San Diego"
    timezone = "America/Los_Angeles"
    start_urls = ["https://sdcounty.granicus.com/ViewPublisher.php?view_id=9"]

    def parse(self, response):
        for item in response.xpath("//tbody/tr")[1:]:
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
                created=datetime.now(),
                updated=datetime.now(),
            )

            if meeting["start"] is None:
                return

            meeting["classification"] = self._parse_classification(meeting["title"])
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        row = item.xpath("td[@class='listItem']/text()")
        text = row[0].extract()
        return text.strip()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, title):
        for classification in CLASSIFICATIONS:
            if classification.lower() in title.lower():
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        row = item.xpath("./td[@class='listItem']/text()")
        if len(row) > 1:
            date = row[1].get()
            try:
                return dateparse(date, fuzzy=True, ignoretz=True)
            except ParserError:
                return None
        else:
            return None

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_links(self, item):
        links = []
        row = item.xpath("td[@class='listItem']")

        if len(row) > 4:
            agenda = row[3].xpath("./a/@href").extract()
            if len(agenda) > 0:
                links.append({"href": "https:" + agenda[0], "title": "Agenda"})

            video = row[4].xpath("./a/@href").extract()
            if len(video) > 0:
                if "javascript:void(0)" in video[0]:
                    click = row[4].xpath(".//@onclick")
                    if len(click) > 0:
                        text = click[0].extract()

                        beg = text.find("('")
                        if beg < 0:
                            return links
                        beg = beg + 2
                        end = text.find("'", beg)
                        if end < 0:
                            return links

                        links.append(
                            {"href": "https:" + text[beg:end], "title": "Video"}
                        )
                else:
                    links.append({"href": "https:" + video[0], "title": "Video"})
            return links
        return links

    def _parse_source(self, response):
        return response.url

    def _parse_location(self, item):
        return {
            "address": "1600 Pacific Highway, San Diego, CA 92101",
            "name": "County Administration Center",
        }
