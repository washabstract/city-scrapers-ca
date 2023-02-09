import re
from datetime import datetime
from urllib.parse import urljoin

from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class LaCountyBosSpider(CityScrapersSpider):
    name = "la_county_bos"
    agency = "Los Angeles"
    sub_agency = "County Board of Supervisors"
    timezone = "America/Los_Angeles"
    start_urls = ["https://bos.lacounty.gov/board-meeting-agendas/"]

    def parse(self, response):
        meetings = response.xpath("//div[@class='meeting-inner-container']")
        for item in meetings:
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

            if meeting["start"] is None:
                return

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting


    def _parse_title(self, item):
        title = item.xpath(".//*[@class='card-title']/text()").get()
        return title

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item):
        return BOARD

    def _parse_start(self, item):
        dts = item.xpath(".//*[@class='meeting-info']//text()").getall()
        dt = "".join(dts)
        try:
            start = dateparse(dt, ignoretz = True)
        except ParserError:
            start = None
        return start

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        return {
            "address": "500 West Temple Street, Los Angeles, California 90012",
            "name": "Kenneth Hahn Hall of Administration",
        }

    def _parse_links(self, item):
        links = []
        card_links = item.xpath(".//a[@class='card-link']")
        for link in card_links:
            href = link.xpath("@href").get()
            title = link.xpath(".//text()").get().strip()
            if "agenda" in title.lower():
                title = "Agenda"
            
            links.append({
                "href": href, "title": title
            })
        return links

    def _parse_source(self, response):
        return response.url
