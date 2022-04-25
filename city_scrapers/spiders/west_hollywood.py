from datetime import datetime

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class WestHollywoodSpider(CityScrapersSpider):
    name = "west_hollywood"
    agency = "West Hollywood"
    timezone = "America/Los_Angeles"
    start_urls = [
        "https://weho.granicus.com/ViewPublisher.php?view_id=22",
        "https://weho.granicus.com/ViewPublisher.php?view_id=31",
    ]

    def parse(self, response):
        for item in response.xpath("//tr[@class='odd'] | //tr[@class='even'] ")[1:]:
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                start=self._parse_start(item, response),
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

            meeting["classification"] = self._parse_classification(
                item, meeting["title"]
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        title = item.xpath(".//td[@headers='Name']//text()")
        if len(title) < 1:
            return ""

        return title[0].extract().strip()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item, title):
        for classification in CLASSIFICATIONS:
            if classification.lower() in title.lower():
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item, response):
        date = item.xpath(
            ".//td[@headers='Date Regular-City-Council-Meeting']/text() |"
            ".//td[@headers='Date Planning-Commission-Meeting']/text()"
        )
        if len(date) < 1:
            return None

        date = date[0].extract().strip()
        if "id=22" in response.url:
            date = date + " 6 PM"
        elif "id=31" in response.url:
            date = date + " 6:30 PM"

        try:
            return dateparse(date, fuzzy=True, ignoretz=True)
        except (ParserError):
            return None

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        result = []
        links = item.xpath(".//td/a[@href]")
        if len(links) < 1:
            return result

        for link in links[1:]:
            # try the href tag for link
            temp = link.xpath("./@href")
            href = ""
            if len(temp) < 1:
                href = ""
            else:
                href = temp[0].extract()

            # if not good, check onclick
            if ".com" not in href:
                click = link.xpath("./@onclick")
                if len(click) > 0:
                    text = click[0].extract()

                    beg = text.find("('")
                    if beg < 0:
                        continue
                    beg = beg + 2
                    end = text.find("'", beg)
                    if end < 0:
                        continue

                    href = text[beg:end]
                    if ".com" not in href:
                        continue
                else:
                    continue

            # Make sure link starts with http
            if href[0:2] == "//":
                href = "http:" + href

            title = link.xpath("./text()")
            if len(title) < 1:
                title = ""
            else:
                title = title[0].extract().strip()

            result.append({"href": href, "title": title})

        return result

    def _parse_source(self, response):
        return response.url
