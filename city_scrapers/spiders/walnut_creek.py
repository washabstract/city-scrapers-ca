import re
from datetime import datetime

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class WalnutCreekSpider(CityScrapersSpider):
    name = "walnut_creek"
    agency = "Walnut Creek"
    sub_agency = "City"
    timezone = "America/Los_Angeles"
    start_urls = ["https://walnutcreek.granicus.com/ViewPublisher.php?view_id=12"]

    def parse(self, response):
        for item in response.xpath("//tbody/tr"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
                created=datetime.now(),
                updated=datetime.now(),
            )
            meeting["classification"] = self._parse_classification(meeting["title"])

            if len(meeting["links"]) > 0 and (
                meeting["links"][0]["title"] == "Agenda"
                or meeting["links"][0]["title"] == "Minutes"
            ):
                url = meeting["links"][0]["href"]
                yield response.follow(
                    url,
                    callback=self._parse_time_location,
                    cb_kwargs={"meeting": meeting, "item": item},
                    dont_filter=True,
                )
            else:
                yield from self._parse_time_location(None, meeting, item)

    def _parse_time_location(self, response, meeting, item):
        meeting["start"], meeting["location"] = (
            self._parse_start(item, response),
            self._parse_location(response, meeting),
        )

        if meeting["start"] is None:
            return

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        yield meeting
        return

    def _parse_title(self, item):
        row = item.xpath("td[@class='listItem']/text()")
        text = row[0].extract()
        return text.strip()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, title):
        for classification in CLASSIFICATIONS:
            if classification.lower() in title.lower():
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item, response):
        row = item.xpath("./td[@class='listItem']/text()")
        if len(row) > 1:
            date = row[1].get()
            if len(row) > 2:
                time = row[2].get()
            else:
                time = ""

            try:
                # Upcoming meetings have start time, but past meetings have duration
                if ("am" in time) or ("pm" in time):
                    dt = dateparse(date + time, fuzzy=True, ignoretz=True)
                else:
                    if (
                        response
                        and response.body != b""
                        and b"text/html" in response.headers.get("Content-Type", "")
                    ):
                        # extract date from response via regex
                        head = response.xpath("//hr/preceding::*/text()")
                        head_txt = ""
                        for line in head:
                            if line.get().strip() != "":
                                head_txt = head_txt + line.get() + "\n"
                        time_reg = time_reg = r"\d?\d:\d\d\s?[ap]m"
                        times = re.findall(time_reg, head_txt, re.IGNORECASE)
                        if len(times) > 0:
                            date = date + " " + times[0]

                    dt = dateparse(date, fuzzy=True, ignoretz=True)
                    # Could do end time w time dif...

                return dt
            except ParserError:
                return None
        else:
            return None

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_links(self, item):
        links = []
        row = item.xpath("td[@class='listItem']")

        # Archived Meetings
        if len(row) > 4:
            agenda = row[3].xpath("./a/@href").extract()
            if len(agenda) > 0:
                name = row[3].xpath("./a/text()").get().lower()
                title = "Minutes" if "minutes" in name else "Agenda"
                links.append({"href": "https:" + agenda[0], "title": title})

            video = row[4].xpath("./a/@href").extract()
            if len(video) > 0:
                name = row[4].xpath("./a/text()").get().lower()
                title = "Audio" if "audio" in name else "Video"
                if "javascript:void(0)" in video[0]:
                    click = row[4].xpath(".//@onclick")
                    if len(click) > 0:
                        text = click[0].extract()

                        beg = text.find("('")
                        if beg < 0:
                            return links
                        beg = beg + 2
                        end = text.find("'", beg)
                        if end < 0:
                            return links

                        links.append({"href": "https:" + text[beg:end], "title": title})
                else:
                    links.append({"href": "https:" + video[0], "title": title})
            return links

        # Upcoming Meetings
        if len(row) > 3:
            agenda = row[3].xpath("./a/@href").extract()
            if len(agenda) > 0:
                links.append({"href": "https:" + agenda[0], "title": "Agenda"})

        return links

    def _parse_source(self, response):
        return response.url

    def _parse_location(self, response, meeting):
        location = {
            "address": "",
            "name": "",
        }

        if (
            response
            and response.body != b""
            and b"text/html" in response.headers.get("Content-Type", "")
        ):
            # Header: search for room name
            head = response.xpath("//hr/preceding::*/text()")
            head_txt = ""
            for line in head:
                if line.get().strip() != "":
                    head_txt = head_txt + line.get() + "\n"

            room_reg = r"council chamber|1st floor/3rd floor conference room|1st floor conference room|3rd floor conference room"  # noqa
            rooms = re.findall(room_reg, head_txt, re.IGNORECASE)
            if len(rooms) > 0:
                room = rooms[0].title()
                location = {
                    "address": room + ", 1666 N Main St, Walnut Creek",
                    "name": room + ", City Hall",
                }

            # Body:
            body = response.xpath("//hr/following::*/text()")
            body_txt = ""
            for line in body:
                if line.get().strip() != "":
                    body_txt = body_txt + line.get() + "\n"

            # if no in person location yet, try searching in body text for it
            if len(rooms) <= 0:
                rooms = re.findall(room_reg, body_txt, re.IGNORECASE)
                if len(rooms) > 0:
                    room = rooms[0].title()
                    location = {
                        "address": room + ", 1666 N Main St, Walnut Creek",
                        "name": room + ", City Hall",
                    }

            # search body text for zoom link
            zoom_reg = r"(?:webinar|zoom meeting)\sid:?\s?\d{3}\s?\d{4}\s?\d{4}.+(?:password|passcode):?\s?\d{3}\s?\d{3}"  # noqa
            zooms = re.findall(zoom_reg, body_txt, re.IGNORECASE)

            if len(zooms) > 0:
                zoom = zooms[0]
                if len(rooms) > 0:
                    meeting["time_notes"] = (
                        "There is also a virtual option for this meeting. " + zoom
                    )
                else:
                    location = {"address": zoom, "name": "Virtual Meeting"}

        return location
