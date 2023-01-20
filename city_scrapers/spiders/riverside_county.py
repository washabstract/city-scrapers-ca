import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class RiversideCountySpider(CityScrapersSpider):
    name = "riverside_county"
    agency = "Riverside"
    sub_agency = "County"
    timezone = "America/Los_Angeles"
    start_urls = ["https://riversidecountyca.iqm2.com/Citizens/calendar.aspx"]
    base_url = "riversidecountyca.iqm2.com"

    def parse(self, response):
        for item in response.css(".MeetingRow"):
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=self._parse_classification(item, title),
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
        """Parse or generate meeting title."""
        title = item.xpath(
            ".//div[@class='RowBottom']/div[@class='MainScreenText RowDetails']/text()"
        ).get()
        if title is not None:
            return title.strip()
        else:
            return ""

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item, title):
        for classification in CLASSIFICATIONS:
            if classification in title:
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        try:
            datetime_start = (
                item.xpath(".//div[@class='RowTop']/div[@class='RowLink']/a/text()")
                .get()
                .strip()
            )
            datetime_start = dateparse(datetime_start)
            return datetime_start.replace(tzinfo=None)
        except ParserError:
            return None

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        return {
            "address": "4080 Lemon Street, Riverside, CA 9250",
            "name": "",
        }

    def _parse_links(self, item):
        results = []
        links = item.xpath(
            ".//div[@class='RowTop']/div[@class='RowRight MeetingLinks']/div/a"
        )
        for link in links:
            href = link.xpath("@href").get()
            title = link.xpath("text()").get()

            if href is None or href == "" or href == "#":
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

                beg = text.find('("')
                if beg < 0:
                    continue
                beg = beg + 2
                end = text.find('"', beg)
                if end < 0:
                    continue

                href = urljoin("https://" + self.base_url, text[beg:end])
                results.append({"href": href, "title": title})
            else:
                parsed = urlparse(href)
                # If there is no scheme we add a https scheme
                if parsed.scheme == "":
                    parsed = parsed._replace(scheme="https")

                # If there is no domain we include it.
                if parsed.netloc == "":
                    parsed = parsed._replace(netloc=self.base_url)

                # Only append if there is a domain
                if parsed.netloc != "":
                    results.append({"href": parsed.geturl(), "title": title})

        return results

    def _parse_source(self, response):
        return response.url
