from datetime import date, datetime

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class LaPlanningSpider(CityScrapersSpider):
    name = "la_planning"
    agency = "LA Planning Commission"
    timezone = "America/Los_Angeles"
    start_urls = [
        "https://planning.lacity.org/dcpapi/meetings/api/all/commissions/"
        f"{date.today().year}",
        "https://planning.lacity.org/dcpapi/meetings/api/all/boards/"
        f"{date.today().year}",
        "https://planning.lacity.org/dcpapi/meetings/api/all/hearings/"
        f"{date.today().year}",
    ]

    def parse(self, response):
        meetings = response.json()["Entries"]
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

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        if "Type" in item and item["Type"]:
            if "BoardName" in item and item["BoardName"]:
                return f"{item['BoardName']} {item['Type']}"
            if "APC" in item and item["APC"]:
                if item["APC"] == "Citywide":
                    return item["Type"]
                return f"{item['APC']} Region {item['Type']}"
        return "LA Planning Commission"

    def _parse_description(self, item):
        if "Description" in item and item["Description"]:
            return item["Description"]
        if "Note" in item and item["Note"]:
            return item["Note"]
        return ""

    def _parse_classification(self, item):
        for classification in CLASSIFICATIONS:
            if classification in item["Note"]:
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        datetime_str = ""
        if "Date" in item and item["Date"]:
            datetime_str += item["Date"]
        if "Time" in item and item["Time"]:
            datetime_str += item["Time"]
        return dateparse(datetime_str) if datetime_str else None

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        if "Address" in item and item["Address"]:
            return {"address": item["Address"], "name": item["Type"]}
        return {"address": "", "name": ""}

    def _parse_links(self, item):
        links = []
        if "AgendaLink" in item and item["AgendaLink"]:
            links.append(
                {"href": item["AgendaLink"], "title": "Meeting/Agenda Information"}
            )
        if "AudioLink" in item and item["AudioLink"]:
            links.append({"href": item["AudioLink"], "title": "Audio"})
        if "MinutesLink" in item and item["MinutesLink"]:
            links.append({"href": item["MinutesLink"], "title": "Minutes"})
        if "HearingLink" in item and item["HearingLink"]:
            links.append({"href": item["HearingLink"], "title": "Hearing Link"})
        if "AddDocsLink" in item and item["AddDocsLink"]:
            links.append(
                {"href": item["AddDocsLink"], "title": "Supplemental Documents"}
            )
        return links if links else [{"href": "", "title": ""}]

    def _parse_source(self, response):
        return response.url
