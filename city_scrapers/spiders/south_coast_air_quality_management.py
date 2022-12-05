from datetime import datetime
from urllib.parse import urljoin

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse

from city_scrapers.items import Meeting


class SouthCoastAirQualityManagementSpider(CityScrapersSpider):
    name = "south_coast_air_quality_management"
    agency = "South Coast"
    sub_agency = "Air Quality Management"
    timezone = "America/Los_Angeles"
    start_urls = [
        "http://www.aqmd.gov/home/news-events/meeting-agendas-minutes?filter=All"
    ]
    base_url = "http://www.aqmd.gov"

    def parse(self, response):
        for item in response.xpath(
            ".//table[@class='FormsList table table-striped']/tbody/tr"
        ):
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

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        # Returning the item cateogry as the title
        item_category = item.xpath(".//td[4]/span/text()").get()
        return item_category.strip()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item):
        item_category = item.xpath(".//td[4]/span/text()").get()
        if "board" in item_category.lower().strip():
            return BOARD
        else:
            return COMMITTEE

    def _parse_start(self, item):
        date_start = item.xpath(".//td[1]/span/text()").get()
        date_start = parse(date_start.strip())

        return date_start.replace(tzinfo=None)

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        return {
            "address": "21865 Copley Dr, Diamond Bar, CA 91765",
            "name": "",
        }

    def _parse_links(self, item):
        agenda_link = item.xpath(".//td[2]/a/@href").get()
        minutes_link = item.xpath(".//td[3]/a/@href").get()

        results = []

        if agenda_link:
            results.append(
                {"title": "Agenda", "href": urljoin(self.base_url, agenda_link.strip())}
            )

        if minutes_link:
            results.append({"title": "Minutes", "href": minutes_link.strip()})

        return results

    def _parse_source(self, response):
        return response.url
