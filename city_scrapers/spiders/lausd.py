from datetime import datetime

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse
from dateutil.parser._parser import ParserError

from city_scrapers.items import Meeting


class LausdSpider(CityScrapersSpider):
    name = "lausd"
    agency = "LA Unified School District"
    timezone = "America/Los_Angeles"
    start_urls = ["http://laschoolboard.org/LAUSDBdMtgAgendas"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath("//div[@id='squeeze-content']//tbody/tr")[1:]:
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

            meeting["classification"] = self._parse_classification(
                item, meeting["title"]
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        cols = item.xpath("./td/text()")
        if len(cols) < 2:
            return ""
        return cols[1].extract().strip()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item, title):
        """Parse or generate classification from allowed options."""
        for classification in CLASSIFICATIONS:
            if classification.lower() in title.lower():
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        cols = item.xpath("./td/a/text()")
        if len(cols) < 1:
            return datetime(1, 1, 1, 0, 0)

        date = cols[0].extract().strip()
        try:
            return dateparse(date, fuzzy=True, ignoretz=True)
        except (ParserError):
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
        result = []
        cols = item.xpath("./td/a")
        if len(cols) < 2:
            return result

        links = cols[1:]
        for link in links:
            href = link.xpath("@href")
            if len(href) < 1:
                continue
            href = href[0].extract().strip()

            name = link.xpath("text()")
            if len(name) < 1:
                name = ""
            else:
                name = name[0].extract().strip()

            result.append({"href": href, "title": name})

        return result

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
