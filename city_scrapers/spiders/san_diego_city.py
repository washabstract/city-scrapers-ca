import pathlib
import re
from datetime import datetime, timedelta
from io import BytesIO
from urllib.parse import urljoin

import pdfplumber
from city_scrapers_core.constants import CITY_COUNCIL, COMMISSION, COMMITTEE
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse
from pdfminer.pdfparser import PDFSyntaxError

from city_scrapers.items import Meeting


class SanDiegoCitySpider(CityScrapersSpider):
    name = "san_diego_city"
    agency = "San Diego"
    sub_agency = "City"
    timezone = "America/Los_Angeles"
    past_meeting_urls = [
        # City council
        "https://sandiego.granicus.com/ViewPublisher.php?view_id=3",
        # Planning commission
        "https://sandiego.granicus.com/ViewPublisher.php?view_id=8",
        # Fire Ad Hoc Committee
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=28",
        # Audit Committee
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=24",
        # Budget and Finance Committee
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=16",
        # Charter Review Committee
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=25",
        # Government Efficiency
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=13",
        # Land use & Housing
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=12",
        # Natural Resources & Culture
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=14",
        # Public Safety and Neighborhood Services Committee
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=15",
        # Rules Committee
        "http://sandiego.granicus.com/ViewPublisher.php?view_id=11",
    ]

    city_council_upcoming = "https://sandiego.hylandcloud.com/211agendaonlinecouncil"
    committees_upcoming = (
        "https://sandiego.hylandcloud.com/"
        "211agendaonlinecomm/Meetings/Search?"
        "dropid=4&mtids=131%2C114%2C119%2C102%"
        "2C116%2C115%2C133%2C122%2C120%2C121%2C132%2C123%2C117%2C127%2C134%2C118"
    )
    planning_commission_upcoming = (
        "https://www.sandiego.gov/planning-commission/documents/agenda"
    )

    upcoming_meetings_urls = [
        # City council
        "https://sandiego.hylandcloud.com/211agendaonlinecouncil",
        # Committees
        "https://sandiego.hylandcloud.com/"
        "211agendaonlinecomm/Meetings/Search?"
        "dropid=4&mtids=131%2C114%2C119%2C102%"
        "2C116%2C115%2C133%2C122%2C120%2C121%2C132%2C123%2C117%2C127%2C134%2C118",
        # Planning commission
        "https://www.sandiego.gov/planning-commission/documents/agenda",
    ]
    upcoming_meeting_base_url = "https://sandiego.hylandcloud.com"

    start_urls = past_meeting_urls + upcoming_meetings_urls

    def parse(self, response):
        if response.url in self.past_meeting_urls:
            # past meetings
            for item in response.xpath(".//tbody/tr"):
                start = self._parse_start(item)
                title = self._parse_title(item)

                meeting = Meeting(
                    title=title,
                    description=self._parse_description(item),
                    classification=self._parse_classification(item, title),
                    start=start,
                    end=self._parse_end(item, start),
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
        else:
            # upcoming
            if response.url == self.planning_commission_upcoming:
                # parsing the agenda and then follow the link
                for agenda_link in response.xpath(
                    "//div[@class='field-items']/.//a/@href"
                ).getall():
                    # Only following pdf links
                    if pathlib.Path(agenda_link).suffix == ".pdf":
                        yield response.follow(
                            agenda_link,
                            callback=self._parse_planning,
                            cb_kwargs={"source": response.url},
                            dont_filter=True,
                        )
            else:
                if response.url == self.city_council_upcoming:
                    # for council meetings
                    item_path = ".//div[@id='meetings-list-upcoming']/div/div"
                else:
                    # for committee meeting
                    item_path = ".//div[@id='meetings-list-content']/div/div/div"

                for item in response.xpath(item_path):
                    # Agenda button contains the time
                    title = self._parse_title_upcoming(item)

                    meeting = Meeting(
                        title=title,
                        description=self._parse_description(item),
                        classification=self._parse_classification(item, title),
                        start=self._parse_start_upcoming(item),
                        end=self._parse_end_upcoming(item),
                        all_day=self._parse_all_day(item),
                        time_notes=self._parse_time_notes(item),
                        location=self._parse_location(item),
                        links=self._parse_links_upcoming(item),
                        source=self._parse_source(response),
                        created=datetime.now(),
                        updated=datetime.now(),
                    )

                    meeting["status"] = self._get_status(meeting)
                    meeting["id"] = self._get_id(meeting)

                    yield meeting

    def _parse_planning(self, response, source):
        if response is not None:
            try:
                with pdfplumber.open(BytesIO(response.body)) as pdf:
                    if len(pdf.pages) > 0:
                        first_page = pdf.pages[0]
                        extracted_text = first_page.extract_text()
                        raw_extracted_text = extracted_text if extracted_text else ""

                        title = self._parse_title_planning_upcoming(raw_extracted_text)
                        meeting = Meeting(
                            title=title,
                            description=self._parse_description(raw_extracted_text),
                            classification=COMMISSION,
                            start=self._parse_start_planning_upcoming(
                                raw_extracted_text
                            ),
                            end=self._parse_end_upcoming(raw_extracted_text),
                            all_day=self._parse_all_day(raw_extracted_text),
                            time_notes=self._parse_time_notes(raw_extracted_text),
                            location=self._parse_location(raw_extracted_text),
                            links=self._parse_links_planning_upcoming(
                                raw_extracted_text, response
                            ),
                            source=source,
                            created=datetime.now(),
                            updated=datetime.now(),
                        )

                        meeting["status"] = self._get_status(meeting)
                        meeting["id"] = self._get_id(meeting)

                        yield meeting
            except PDFSyntaxError:
                # Do nothing
                pass

    def _parse_title(self, item):
        title = item.xpath(".//td[1]/text()").get()
        return title

    def _parse_title_upcoming(self, item):
        agenda_title = item.xpath("//div[@class='six columns']/p/text()").get()
        if agenda_title is None:
            agenda_title = ""
        return agenda_title

    def _parse_title_planning_upcoming(self, item):
        return "Planning Commission"

    def _parse_description(self, item):
        "No description"
        return ""

    def _parse_classification(self, item, title):
        """Parse or generate classification from allowed options."""
        title_lower = title.lower()
        if "commission" in title_lower:
            return COMMISSION
        elif (
            "committee" in title_lower
            or "government efficiency" in title_lower
            or "natural resources" in title_lower
            or "public safety" in title_lower
        ):
            return COMMITTEE
        else:
            return CITY_COUNCIL

    def _parse_start_upcoming(self, item):

        agenda_button_title = item.xpath("//a/@title").get()
        # Use regex to parse start time
        time_regex = r"\son\s(?P<datetime>.*)$"
        results = re.search(time_regex, agenda_button_title)

        if results:
            start_str = results.group("datetime")
            if start_str:
                start = parse(start_str)
                return start.replace(tzinfo=None)

        return None

    def _parse_start_planning_upcoming(self, item):
        start_time = re.search(
            r".+[0-9]{4},?\s+at\s+\d{,2}:\d{,2}\s+"
            r"(A\.?M\.?)?(P\.?M\.?)?(a\.?m\.?)?(p\.?m\.?)?",
            item,
            re.M,
        )

        if start_time:
            start_time = start_time.group().strip()
            return parse(start_time).replace(tzinfo=None)

        return None

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_date_str = item.xpath(".//td[2]/text()").get()
        start = parse(start_date_str)
        return start.replace(tzinfo=None)

    def _parse_end(self, item, start: datetime):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        meeting_length = item.xpath(".//td[3]/text()").get()

        match_regex = r"(?P<hours>\d+)\shr\s(?P<mins>\d+)\smin"
        hours_mins_match = re.search(match_regex, meeting_length)

        # Try to typecast
        if hours_mins_match:
            try:
                hours, mins = hours_mins_match.group("hours", "mins")
                hours = int(hours)
                mins = int(mins)
                delta = timedelta(hours=hours, minutes=mins)
                end = start + delta
                return end
            except ValueError:
                pass

        return None

    def _parse_end_upcoming(self, item):
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
            "address": (
                "City Council Chambers - 12th Floor,"
                " 202 C Street San Diego, CA 92101"
            ),
            "name": "City Administration Building",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        results = []
        video1 = item.xpath(".//td[4]/a/@onclick").get()  # inside a window.open
        column1 = item.xpath(".//td[5]/a")
        column2 = item.xpath(".//td[6]/a")
        column3 = item.xpath(".//td[7]/a")

        if video1 is not None:
            # Extracting the url from the onclick function
            url_match = r"'(?P<url>//.*?)'"
            video1 = re.search(url_match, video1)
            if video1:
                video1 = video1.group("url")
                results.append({"title": "Video", "href": urljoin("https:", video1)})

        for column in [column1, column2, column3]:
            if column:
                href_text = column.xpath("text()").get()
                href_link = column.xpath("@href").get()

                if href_text.lower() == "minutes":
                    results.append(
                        {"title": href_text, "href": urljoin("https:", href_link)}
                    )
                else:
                    results.append({"title": href_text, "href": href_link})

        return results

    def _parse_links_upcoming(self, item):
        results = []
        for link in item.xpath(".//a"):
            link_href = link.xpath("./@href").get()
            link_title = link.xpath("./text()").get()
            results.append(
                {
                    "title": link_title,
                    "href": urljoin(self.upcoming_meeting_base_url, link_href),
                }
            )

        return results

    def _parse_links_planning_upcoming(self, item, response):
        return [
            {
                "title": "Agenda",
                # the response url is the agenda link
                "href": response.url,
            }
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
