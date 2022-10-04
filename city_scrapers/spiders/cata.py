from datetime import datetime

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CataSpider(CityScrapersSpider):
    name = "cata"
    agency = "California Transportation Commission"
    timezone = "America/Los_Angeles"
    start_urls = ["https://catc.ca.gov/meetings-events/commission-meetings"]

    def parse(self, response):
        meetings_raw = response.xpath("//hr/following::h3")
        for first in meetings_raw:
            siblings = first.xpath("following-sibling::*")
            i = 0
            item = [first]
            num_sibs = len(siblings)
            while i < num_sibs and siblings[i].get() != "<hr>":
                item.append(siblings[i])
                i+=1

            print(len(item))
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                # classification=self._parse_classification(item),
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
            meeting["classification"] = self._parse_classification(meeting["title"])
            # meeting["start"] = self._parse_start(item, meeting["title"])

            # if meeting["start"] is None:
            #     return

            # meeting["status"] = self._get_status(meeting)
            # meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        title = item[0].xpath("text()")
        if title:
            return title.get().strip()
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, title):
        for classification in CLASSIFICATIONS:
            if classification.lower() in title.lower():
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

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
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
