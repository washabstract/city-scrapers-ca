from datetime import datetime
from html import unescape
from urllib.parse import urljoin

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse
from dateutil.parser._parser import ParserError


class SantaMonicaSpider(CityScrapersSpider):
    name = "santa_monica"
    agency = "Santa Monica City Council"
    timezone = "America/Los_Angeles"
    start_urls = ["http://santamonicacityca.iqm2.com/Citizens/calendar.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
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
            )

            meeting["classification"] = self._parse_classification(item)
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
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        title = item.xpath(".//div[@class='MainScreenText RowDetails']/text()")
        title = title.extract()
        if len(title) < 1:
            title = ""
        else:
            title = title[0]

        for classification in CLASSIFICATIONS:
            if classification in title:
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        dt = item.xpath(".//div[@class='RowLink']//text()")
        dt = dt.extract()
        if len(dt) < 1:
            return datetime(1, 1, 1, 0, 0)

        try:
            return dateparse(dt[0], fuzzy=True, ignoretz=True)
        except ParserError:
            return datetime(1, 1, 1, 0, 0)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {}

    def _parse_links(self, item):
        """Parse or generate links."""
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
        """Parse or generate source."""
        return response.url
