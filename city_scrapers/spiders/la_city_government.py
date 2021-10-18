from datetime import date, datetime, timedelta
from html import unescape

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError, parse

from city_scrapers.items import Meeting


class LaCityGovernmentSpider(CityScrapersSpider):
    name = "la_city_government"
    agency = "Los Angeles City Government"
    timezone = "America/Los_Angeles"
    start_urls = [
        (
            "https://calendar.lacity.org/rest/views/calendar_rest_dynamic"
            "?display_id=services_1"
            "&display_id=services_1"
            "&filters%5Beventtype%5D=686"
            "&filters%5Bdepartment%5D="
            "&filters%5Btags%5D="
            "&filters%5Bstart%5D%5Bvalue%5D%5Bdate%5D="
            f"{str(date.today()-timedelta(days=14))}"
            "&filters%5Bend%5D%5Bvalue%5D%5Bdate%5D="
            f"{str(date.today()+timedelta(days=14))}"
        ),
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self.logger.info("Parse function called on %s", response.url)
        json_response = response.json()
        for item in json_response:
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

            meeting["id"] = self._get_id(meeting)
            meeting["status"] = self._get_status(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = ""
        if "rawtitle" in item and item["rawtitle"]:
            title = unescape(item["rawtitle"])
        elif "title" in item and item["title"]:
            title = unescape(item["title"])
        return title.strip()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        description = ""
        if "descriptionraw" in item and item["descriptionraw"]:
            description = unescape(item["descriptionraw"])
        elif "description" in item and item["description"]:
            description = unescape(item["description"])
        return description.strip()

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        for classification in CLASSIFICATIONS:
            if classification in unescape(item["rawtitle"]):
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start = None
        fields = ["start", "event-date-field-start", ["event-date", "event-time"]]
        for field in fields:
            start_str = ""
            if type(field) is list:
                for f in field:
                    if f in item and item[f]:
                        start_str += f"{item[f]} "
            else:
                if field in item and item[field]:
                    start_str = item[field]
            try:
                start = parse(start_str)
            except ParserError:
                continue
            return start.replace(tzinfo=None)
        return start.replace(tzinfo=None)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        end = None
        if "end" in item and item["end"]:
            try:
                end = parse(item["end"]).replace(tzinfo=None)
            except ParserError:
                pass
        if self._parse_start(item) == end:
            return None
        return end.replace(tzinfo=None)

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        if "multiday" in item and item["multiday"] == "Yes":
            return "This is a multiday event."
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        name = item["organization"]
        address = ""
        if "street" in item and item["street"]:
            address += item["street"] + ", "
        if "street2" in item and item["street2"]:
            address += item["street2"] + ", "
        if "city" in item and item["city"]:
            address += item["city"] + ", "
        if "state" in item and item["state"]:
            address += item["state"] + ", "
        if "country" in item and item["country"]:
            address += item["country"] + " "
        if "zipcode" in item and item["zipcode"]:
            address += item["zipcode"]
        return {
            "address": address.strip() if address else "",
            "name": name.strip() if name else "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        if "informationurl" in item and item["informationurl"]:
            links.append(
                {"href": item["informationurl"], "title": "Meeting/Agenda Information"}
            )
        if "url" in item and item["url"]:
            links.append({"href": item["url"], "title": "Calendar Link"})
        if len(links) == 0:
            links.append({"href": "", "title": ""})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
