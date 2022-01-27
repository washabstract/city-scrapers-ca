from urllib.parse import urljoin

from datetime import datetime
from city_scrapers_core.constants import TENTATIVE, BOARD, COMMITTEE, COMMISSION
from city_scrapers.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class LaPortSpider(CityScrapersSpider):
    name = "la_port"
    agency = "Port of LA"
    timezone = "America/Los_Angeles"
    start_urls = ["https://portofla.granicus.com/ViewPublisher.php?view_id=9"]

    # Not that important?? It's only useed in datetime
    def parse(self, response):
        items = response.xpath("//tbody/tr")
        for item in items:
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
                created=datetime.now(),
                updated=datetime.now(),
            )

            meeting["status"] = TENTATIVE#self._get_status(meeting)
            meeting["id"] = ""# self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        row = item.xpath("td[@class='listItem']/text()")
        return row[0].get()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item):
        row = item.xpath("td[@class='listItem']/text()")
        title = (row[0].get()).lower()
        if "committee" in title:
            return COMMITTEE
        elif "commission" in title:
            return COMMISSION
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        row = item.xpath("td[@class='listItem']/text()")
        date = row[1].get()
        if len(row) > 5:
            return datetime(2020, 4, 20, 0, 0)

        dt = datetime.strptime(date, "%B %d, %Y")
        return dt


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
