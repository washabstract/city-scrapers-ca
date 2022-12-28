from datetime import datetime

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class LausdSpider(CityScrapersSpider):
    name = "lausd"
    agency = "Los Angeles"
    sub_agency = "Unified School District"
    timezone = "America/Los_Angeles"
    start_urls = ["http://laschoolboard.org/LAUSDBdMtgAgendas"]

    def parse(self, response):
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

            if meeting["start"] is None:
                return

            meeting["classification"] = self._parse_classification(
                item, meeting["title"]
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        cols = item.xpath("./td/text()")
        if len(cols) < 2:
            return ""
        return cols[1].extract().strip()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item, title):
        for classification in CLASSIFICATIONS:
            if classification.lower() in title.lower():
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        cols = item.xpath("./td/a/text()")
        if len(cols) < 1:
            return None

        date = cols[0].extract().strip()
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
        return response.url
