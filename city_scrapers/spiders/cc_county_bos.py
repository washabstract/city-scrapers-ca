from datetime import date, datetime
from urllib.parse import urljoin

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class CcCountyBosSpider(CityScrapersSpider):
    name = "cc_county_bos"
    agency = "Contra Costa"
    sub_agency = "County Board of Supervisors"
    timezone = "America/Los_Angeles"
    start_urls = [
        "http://64.166.146.245/agenda_publish.cfm"
        f"?id=&mt=ALL&get_month={date.today().month}&get_year={date.today().year}"
    ]
    base_url = "http://64.166.146.245"

    def parse(self, response):
        meeting_table = response.css("#list tbody")

        for item in meeting_table.css("tr"):

            # Skipping the row that indicates a future date
            row_text = "".join(item.xpath("(.//td)/text()").getall()).strip().lower()
            if "indicates a future date" in row_text:
                continue

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
                created=datetime.now(),
                updated=datetime.now(),
            )

            meeting["classification"] = self._parse_classification(
                item, meeting["title"]
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        # Second column is meeting title
        title = item.xpath("(.//td)[2]/text()").get()
        if title is None:
            title = ""
        return title.strip()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item, title):
        for classification in CLASSIFICATIONS:
            if classification.lower() in title.lower():
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        # First column is the date
        start_str = ""
        # Checking if a link exists
        link_str = item.xpath("(.//td)[1]/a/text()").get()
        if link_str is not None:
            start_str += link_str.strip()
        else:
            # Extracting just the text
            date_str = item.xpath("(.//td)[1]/text()").get()
            if date_str is not None:
                start_str += date_str.strip()
        return dateparse(start_str)

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        return {
            "address": "1025 Escobar Street, Martinez, CA 94553",
            "name": "",
        }

    def _parse_links(self, item):
        results = []

        # Links can appear on the date, minutes and other links
        # Capturing all the links
        links = item.xpath("(.//td)/a/@href").getall()
        title_for_links = item.xpath("(.//td)/a/text()").getall()

        # Mapping to the appropriate format
        for title, link in zip(title_for_links, links):
            if title.lower() == "minutes":
                results.append(
                    {"href": urljoin(self.base_url, link), "title": "Minutes"}
                )
            elif title.lower() == "video":
                results.append({"href": link, "title": "Video Link"})
            else:
                results.append(
                    {
                        "href": urljoin(self.base_url, link),
                        "title": "Meeting/Agenda Information",
                    }
                )

        return results

    def _parse_source(self, response):
        return response.url
