from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse
from dateutil.parser._parser import ParserError


class LawaSpider(CityScrapersSpider):
    name = "lawa"
    agency = "LA World Airports"
    timezone = "America/Los_Angeles"
    start_urls = ["http://lawa.granicus.com/ViewPublisher.php?view_id=4"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath("//div[@class='archive'][2]//tbody//tr"):
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
            )

            meeting["classification"] = self._parse_classification(
                item, meeting["title"]
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = item.xpath("./td[@headers='Name']/text()")
        size = len(title)
        if size < 1:
            return ""
        return title[size - 1].extract().strip()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item, title):
        """Parse or generate classification from allowed options."""
        if "committee" in title.lower():
            return COMMITTEE
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object.
        Default start times:
        regular board meeting - 10am
        security committee - 12pm
        audit committee - 12:30pm"""
        title = item.xpath("./td[@headers='Name']/@id")
        date_tag = ""
        if len(title) >= 1:
            date_tag = title[0].extract()

        path = "./td[@headers='Date " + date_tag + "']/text()"
        date = item.xpath(path)
        if len(date) < 1:
            return datetime(1, 1, 1, 0, 0)

        date_text = date[0].extract().strip()

        if "special" in date_tag.lower():
            pass
        elif "audit" in date_tag.lower():
            date_text = date_text + " 12:30pm"
        elif "security" in date_tag.lower():
            date_text = date_text + " 12pm"
        elif "regular" in date_tag.lower():
            date_text = date_text + " 10am"

        try:
            return dateparse(date_text, fuzzy=True, ignoretz=True)
        except (ParserError):
            return datetime(1, 1, 1, 0, 0)

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
        """Parse or generate location.
        Sets default for committee meetings"""
        title = item.xpath("./td[@headers='Name']/@id")
        date_tag = ""
        if len(title) >= 1:
            date_tag = title[0].extract()

        if ("audit" in date_tag.lower()) | ("security" in date_tag.lower()):
            return {
                "address": "Los Angeles International Airport, 1 World Way, "
                "Los Angeles, CA 90045",
                "name": "Samuel Greenberg Board Room, "
                "Clifton A. Moore Administration Building",
            }

        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = item.xpath(".//td/a[@href]")
        if len(links) < 1:
            return []

        result = []
        for link in links:
            # try the href tag for link
            temp = link.xpath("./@href")
            href = ""
            if len(temp) < 1:
                href = ""
            else:
                href = temp[0].extract()

            # if not good, check onclick
            if ".com" not in href:
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

                    href = text[beg:end]
                    if ".com" not in href:
                        continue
                else:
                    continue

            # Make sure link starts with http
            if href[0:2] == "//":
                href = "http:" + href

            title = link.xpath("./text()")
            if len(title) < 1:
                title = ""
            else:
                title = title[0].extract().strip()

            result.append({"href": href, "title": title})

        return result

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
