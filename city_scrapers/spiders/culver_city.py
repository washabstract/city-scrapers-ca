from datetime import datetime
import re

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class CulverCitySpider(LegistarSpider):
    name = "culver_city"
    agency = "Culver City"
    timezone = "America/Los_Angeles"
    start_urls = ["https://culver-city.legistar.com/Calendar.aspx"]
    # Add the titles of any links not included in the scraped results
    link_types = []

    def parse_legistar(self, events):
        """
        `parse_legistar` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for event in events:
            meeting = Meeting(
                title=event["Name"]["label"],
                description=self._parse_description(event),
                classification=self._parse_classification(event),
                start=self.legistar_start(event),
                end=self._parse_end(event),
                all_day=self._parse_all_day(event),
                time_notes=self._parse_time_notes(event),
                location=self._parse_location(event),
                links=self.legistar_links(event),
                source=self.legistar_source(event),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting
    
    def legistar_start(self, item):
        """Pulls the start time from a Legistar item

        :param item: Scraped item from Legistar
        :return: Meeting start datetime
        """

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
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        title = item["Name"]["label"].title()
        for classification in CLASSIFICATIONS:
            if classification in title:
                return classification
        return NOT_CLASSIFIED

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
        location = item["Meeting Location"]
        clean_location = re.sub("\r\n", " ", location)
        clean_location = re.sub("\xa0", " ", clean_location)
        is_address = bool(re.findall("[0-9]+", clean_location))
        if is_address:
            return {"address": clean_location, "name": ""}
        return {"address": "", "name": clean_location}
