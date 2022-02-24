import re
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMISSION, COMMITTEE
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse
from dateutil.parser._parser import ParserError
from scrapy.exceptions import DropItem, NotSupported

from city_scrapers.items import Meeting


class LaPortSpider(CityScrapersSpider):
    name = "la_port"
    agency = "Port of LA"
    timezone = "America/Los_Angeles"
    start_urls = ["https://portofla.granicus.com/ViewPublisher.php?view_id=9"]

    def parse(self, response):
        for item in response.xpath("//tbody/tr"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
                created=datetime.now(),
                updated=datetime.now(),
            )

            if len(meeting["links"]) > 0 and meeting["links"][0]["title"] == "Agenda":
                yield response.follow(
                    meeting["links"][0]["href"],
                    callback=self._parse_time_location,
                    cb_kwargs={"meeting": meeting, "item": item},
                    dont_filter=True,
                )
            else:
                yield from self._parse_time_location(None, meeting, item)

    def _parse_time_location(self, response, meeting, item):
        """Meeting page url processing.  Scrapes start time and location from meeting
        agenda page
        """
        if (
            response
            and response.body != b""
            and b"text/html" in response.headers.get("Content-Type", "")
        ):
            meeting["start"], meeting["location"] = self._parse_start(
                item, response
            ), self._parse_location(response)
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting
            return

        # If there is no meeting agenda link, scrape time from table
        location = {"address": "", "name": ""}
        row = item.xpath("td[@class='listItem']/text()")
        if len(row) > 0:
            date = row[1].get()
            meeting["start"], meeting["location"] = dateparse(date), location
        else:
            meeting["start"], meeting["location"] = datetime(1, 1, 2, 0, 0), location
        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        yield meeting

    def _parse_title(self, item):
        row = item.xpath("td[@class='listItem']/text()")
        text = row[0].extract()
        return text.strip()

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

    def _parse_start(self, item, response):
        """Calendar page does not have times.  Times can be found in agenda.
        If time cannot be scraoped, defaults to 00:00
        """
        # Try to find the date in the second block of text
        #   If it cannot be found, check the entire intro block
        #   otherwise, just return default 00:00 start time
        try:
            items = response.xpath(
                "//div[@id='contentBody']//div[@id='section-about']//strong"
            )
            if len(items) > 2:
                starttime = "".join(items[2].xpath("text()").getall())
                return dateparse(starttime, fuzzy=True, ignoretz=True)
            elif len(items) > 0:
                raise ValueError
            return datetime(1, 1, 2, 0, 0)
        except (ParserError, ValueError):
            row = item.xpath("td[@class='listItem']/text()")
            if len(items) > 0:
                date = row[1].get()
                return dateparse(date)
            return datetime(1, 1, 2, 0, 0)
        except NotSupported:
            raise DropItem

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_links(self, item):
        links = []
        """Parse or generate links."""
        # For upcoming meetings
        row = item.xpath("td[@class='listItem']")

        # Archived meetings
        if len(row) > 4:
            agenda = row[3].xpath("./a/@href").extract()
            if len(agenda) > 0:
                links.append({"href": "https:" + agenda[0], "title": "Agenda"})

            minutes = row[4].xpath("./a/@href").extract()
            if len(minutes) > 0:
                links.append({"href": "https:" + minutes[0], "title": "Minutes"})

            recording = row[5].xpath("./a").extract()
            if len(recording) > 0:
                # extract the url from the onclick field
                text = recording[0]
                beg = text.find("onclick=\"window.open('") + 22
                end = text.find("'", beg)
                url = text[beg:end]
                clean_url = re.sub("amp;", "", url)
                links.append(
                    {"href": "https:" + clean_url, "title": "Audio/Video Recording"}
                )
            return links

        # Upcoming Meetings
        agenda = row[2].xpath("./*").extract()
        if agenda != []:
            # extract the url from the onclick field
            text = agenda[0]
            beg = text.find("onclick=\"window.open('") + 22
            end = text.find("'", beg)
            url = text[beg:end]
            clean_url = re.sub("amp;", "", url)
            links.append({"href": "https:" + clean_url, "title": "Agenda"})

        return links

    def _parse_location(self, response):
        """The location can be found in the agenda (url extracted from _parse_links)"""
        items = response.xpath(
            "//div[@id='contentBody']//div[@id='section-about']//strong"
        )
        if len(items) > 0:
            location = "".join(items[0].xpath("text()").getall())
            clean_location = re.sub("\r\n", "\n", location)
            clean_location = re.sub("\xa0", " ", clean_location)

            end = clean_location.find("\n")
            if end == -1:
                name = clean_location
                address = ""
            else:
                name = clean_location[:end].strip()
                address = clean_location[end:].strip()

            return {"name": name, "address": address}
        return {"name": "", "address": ""}

    def _parse_source(self, response):
        return response.url
