from datetime import datetime

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class LaCityCouncilSpider(CityScrapersSpider):
    name = "la_city_council"
    agency = "Los Angeles City Council"
    timezone = "America/Chicago"
    start_urls = [
        # "https://www.lacity.org/government/popular-information/"
        # "elected-officials/city-council",
        "https://www.lacity.org/government/meeting-calendars/"
        "city-council-meetingsagendas",
        # "https://www.lacity.org/government/meeting-calendars/"
        # "council-and-committee-meetings"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".event-panel"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            print(meeting)
            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css(".event-panel-title div::text").extract_first()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_date = datetime.strptime(
            item.css(".event-panel-datetime::text").extract_first(), "%b %d, %I:%M %p"
        )
        start_date = start_date.replace(year=datetime.now().year)
        return start_date

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
        address = item.css(".event-panel-address::text").extract_first()
        name = item.css(".event-panel-organization::text").extract_first()
        return {
            "address": address if address else "",
            "name": name if name else "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
