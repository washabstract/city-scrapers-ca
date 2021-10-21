from datetime import date, datetime
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
            "https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings"
            f"?year={date.today().year}"
        ),
        "https://lacity.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings",
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
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
        if "title" in item and item["title"]:
            title = unescape(item["title"])
        return title.strip()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        description = ""
        if "allowPublicSpeaker" in item:
            allowPublicSpeaker = (
                "allows" if item["allowPublicSpeaker"] else "does not allow"
            )
            description += f"This meeting {allowPublicSpeaker} public speakers. "
        if "allowPublicComment" in item:
            allowPublicComment = (
                "allows" if item["allowPublicComment"] else "does not allow"
            )
            description += f"This meeting {allowPublicComment} public speakers. "
        if "isZoomMeeting" in item and item["isZoomMeeting"]:
            description += "This meeting is a Zoom meeting. "
        if "meetingStatus" in item and item["meetingState"] == 1:
            description += "This meeting has been cancelled. "
        return description.strip()

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        for classification in CLASSIFICATIONS:
            if classification in unescape(item["title"]):
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_str = ""
        if "date" in item:
            start_str += item["date"] + " "
        if "time" in item:
            start_str += item["time"]
        try:
            start = parse(start_str)
        except ParserError:
            start = None
        return start.replace(tzinfo=None)

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
        links = []
        if "documentList" in item:
            for doc in item["documentList"]:
                if "compileOutputType" in doc and doc["compileOutputType"] == 1:
                    link = "https://lacity.primegov.com/Public/CompiledDocument/" + str(
                        doc["id"]
                    )
                else:
                    link = (
                        "https://lacity.primegov.com/Portal/Meeting"
                        "?compiledMeetingDocumentFileId=" + str(doc["id"])
                    )

                if "templateName" in doc and doc["templateName"]:
                    title = doc["templateName"]
                else:
                    title = "Meeting/Agenda Information"
                links.append({"href": link, "title": title})
        if "videoUrl" in item and item["videoUrl"]:
            links.append({"href": item["videoUrl"], "title": "Video Link"})
        if len(links) == 0:
            links.append({"href": "", "title": ""})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
