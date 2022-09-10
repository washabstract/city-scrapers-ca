from datetime import datetime
from html import unescape
from urllib.parse import urljoin

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class SantaMonicaSpider(CityScrapersSpider):
    name = "santa_monica"
    agency = "Santa Monica"
    sub_agency = "City Council"
    timezone = "America/Los_Angeles"
    start_urls = [
        # "https://santamonicacityca.iqm2.com/Citizens/calendar.aspx?"
        # "From=1/1/1900&To=12/31/9999"
    ]

    def parse(self, response):
        for item in response.xpath(
            "//div[@class='Row MeetingRow'] | //div[@class='Row MeetingRow Alt']"
        ):
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

            meeting["classification"] = self._parse_classification(
                item, meeting["title"]
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        title = item.xpath(".//div[@class='MainScreenText RowDetails']/text()")
        title = title.extract()
        if len(title) < 1:
            return ""
        else:
            return title[0]

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item, title):
        title = title.lower()

        for classification in CLASSIFICATIONS:
            if classification.lower() in title:
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        dt = item.xpath(".//div[@class='RowLink']//text()")
        dt = dt.extract()
        if len(dt) < 1:
            return None

        try:
            return dateparse(dt[0], fuzzy=True, ignoretz=True)
        except ParserError:
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
        links = item.xpath(".//a[@class='']")
        result = []
        base_url = "https://santamonicacityca.iqm2.com/Citizens/calendar.aspx"
        for link in links:
            new_url = link.xpath("@href").extract()[0]
            href = urljoin(base_url, unescape(new_url))
            title = link.xpath("text()").extract()[0]
            temp = {"href": href, "title": title}
            result.append(temp)

        return result

    def _parse_source(self, response):
        return response.url
