import re
from datetime import datetime, timedelta
from parser import ParserError

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse

from city_scrapers.items import Meeting


class CaHighspeedRailSpider(CityScrapersSpider):
    name = "ca_highspeed_rail"
    agency = "California"
    sub_agency = "High-Speed Rail Authority"
    timezone = "America/Los_Angeles"
    start_urls = [
        "https://hsr.ca.gov/about/board-of-directors/schedule/",
        "https://hsr.ca.gov/about/board-of-directors/finance-audit-committee/",
        "https://hsr.ca.gov/about/board-of-directors/special-matters-committee/",
    ]

    def parse(self, response):
        # Upcoming meetings
        for item in response.xpath(
            "//div[@class='et_pb_module et_pb_text et_pb_text_0  "
            "et_pb_text_align_left et_pb_bg_layout_light']//li/text()"
        ).getall():
            start_date = self._parse_start(item)
            # If in the future then we yield
            # (this list could include meetings in the past)
            if start_date >= datetime.now():
                meeting = Meeting(
                    title=self._parse_title(item, response),
                    description=self._parse_description(item),
                    classification=self._parse_classification(item, response),
                    start=start_date,
                    end=self._parse_end(item),
                    all_day=self._parse_all_day(item),
                    time_notes=self._parse_time_notes(item),
                    location=self._parse_location(item),
                    links=[],
                    source=self._parse_source(response),
                    created=datetime.now(),
                    updated=datetime.now(),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

        # Archived meetings
        for item in response.xpath(
            "//div[contains(@class, 'et_pb_module et_pb_toggle')]"
        ):
            meeting = Meeting(
                title=self._parse_title(item, response),
                description=self._parse_description(item),
                classification=self._parse_classification(item, response),
                start=self._parse_start_archived(item),
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

    def _parse_title(self, item, response):
        if "finance" in response.url:
            return "Finance & Audit Committee"
        elif "special" in response.url:
            return "Special Matters Committee"
        else:
            return "Board Meeting"

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item, response):
        if "committee" in response.url:
            return COMMITTEE
        else:
            return BOARD

    def _parse_start(self, item):
        start_time = timedelta(hours=10)
        regex_date = r"^.*?\d{4}"
        date_match = re.search(regex_date, item, re.M)
        if date_match:
            try:
                date = parse(date_match.group().strip()) + start_time
                return date.replace(tzinfo=None)
            except ParserError:
                return None

        return None

    def _parse_start_archived(self, item):
        date = item.xpath(".//h2/text()").get()
        return self._parse_start(date)

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        return {
            "address": "770 L Street, Suite 620 Sacramento, CA 95814",
            "name": "California High-Speed Rail Authority",
        }

    def _parse_links(self, item):

        links = item.xpath(".//a")
        results = []

        for link in links:
            link_text = link.xpath(".//text()").get()
            href = link.xpath(".//@href").get()

            results.append({"title": link_text, "href": href})

        return results

    def _parse_source(self, response):
        return response.url
