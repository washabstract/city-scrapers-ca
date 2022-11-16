import re
from datetime import datetime, timedelta
from typing import Iterable
from urllib.parse import urljoin, urlparse

import scrapy
from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class GranicusSpider(CityScrapersSpider):
    """
    Subclass of :class:`CityScrapersSpider` that handles processing Granicus sites,
    which almost always share the same components and general structure.

    Any methods that don't pull the correct values can be replaced.
    """

    timezone = "America/Los_Angeles"
    classifications = dict([(c.lower(), c) for c in CLASSIFICATIONS])

    def __init__(self, name=None, agency=None, sub_agency=None, *args, **kwargs):
        self.name = name
        self.agency = agency
        self.sub_agency = sub_agency
        super().__init__(*args, **kwargs)

    def parse(self, response: scrapy.http.Response) -> Iterable[scrapy.Request]:
        # table classes
        # .listingTable
        # .listingTableUpcoming
        tables = response.xpath(
            ".//table[@class='listingTable' or @class='listingTableUpcoming']"
        )

        # Parse the row based on the headers
        for table in tables:
            # parse headers
            headers = table.xpath("thead//th/text()").getall()

            # Converting to a dict mapping to the indexes. E.g. "Name" -> 0
            headers = dict(zip(headers, range(1, len(headers) + 1)))

            for item in table.xpath("tbody//tr"):
                title = self._parse_title(item, headers)

                try:

                    start_datetime = self._parse_start(item, headers)
                except ParserError:
                    # continuing if scraper cannot parse the start time
                    continue

                meeting = Meeting(
                    title=title,
                    description=self._parse_description(item),
                    classification=self._parse_classification(item, title),
                    start=start_datetime,
                    end=self._parse_end(item, start_datetime, headers),
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

    def _parse_title(self, item, headers):
        """Parse or generate meeting title."""
        # try to grab from the hear

        title = item.xpath("td[contains(@headers, 'Name')]/text()").get()
        if title is None:
            # Try to get title from the header
            title_index = (
                headers["Name"] if "Name" in headers else headers.get("Meeting", -1)
            )
            if title_index >= 0:
                title = item.xpath(f"td[{title_index}]/text()").get()
            else:
                # Default to empty title
                title = ""

        title = re.sub(r"\s+", " ", title).strip()
        return title

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item, title):
        # check if any classification matches
        title_lower = title.lower()

        # Loop through all classifications
        for class_text, classification in self.classifications.items():
            if class_text in title_lower:
                return classification

        return NOT_CLASSIFIED

    def _parse_start(self, item, headers):
        """Parse start datetime as a naive datetime object."""
        # getall since the date is split
        date = item.xpath("td[contains(@headers, 'Date')]/text()").getall()
        if len(date) == 0:
            # Default date index is 2
            date_index = headers["Date"] if "Date" in headers else 2
            if date_index >= 0:
                date = item.xpath(f"td[{date_index}]/text()").getall()
            else:
                date = []

        # Converting to str
        date = " ".join(date)
        # Removing the spaces
        date = re.sub(r"\s+", " ", date)
        # Parsing
        date = dateparse(date.strip()).replace(tzinfo=None)
        return date

    def _parse_end(self, item, start, headers):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""

        duration = item.xpath("td[contains(@headers, 'Duration')]/text()").get()
        if duration is None:
            duration_index = headers["Duration"] if "Duration" in headers else -1
            if duration_index >= 0:
                duration = item.xpath(f"td[{duration_index}]/text()").get()
            else:
                duration = None

        if duration is None:
            return None
        else:
            time = re.sub("\xa0", " ", duration)

            hr = 0
            min = 0

            h = time.find("h")
            if h >= 2:
                hr = int(time[h - 2 : h])
            m = time.find("m")
            if m >= 2:
                min = int(time[m - 2 : m])

            length = timedelta(minutes=min, hours=hr)
            return start + length

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
        results = []
        links = item.xpath(".//a")
        if len(links) < 1:
            return results

        for link in links:
            href = link.xpath("@href").get()
            title = link.xpath("text()").get()

            if href is None:
                continue

            if title is None:
                title = ""

            # Cleaning the title.
            # Removing multiple spaces within the title and and the tails
            title = re.sub(r"\s+", " ", title)
            title = title.strip()

            click = link.xpath("./@onclick")
            if len(click) > 0:
                text = click[0].extract()

                beg = text.find("('")
                if beg < 0:
                    continue
                beg = beg + 2
                end = text.find("'", beg)
                if end < 0:
                    continue

                href = urljoin("https:", text[beg:end])
                results.append({"href": href, "title": title})
            else:
                parsed = urlparse(href)
                # If there is no scheme we add a https scheme
                if parsed.scheme == "":
                    href = urljoin("https:", href)

                # Only append if there is a domain
                if parsed.netloc != "":
                    results.append({"href": href, "title": title})

        return results

    def _parse_source(self, response):
        return response.url
