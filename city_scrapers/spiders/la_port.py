import re
from datetime import datetime

import requests
from city_scrapers_core.constants import BOARD, COMMISSION, COMMITTEE
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse
from lxml import html

from city_scrapers.items import Meeting


class LaPortSpider(CityScrapersSpider):
    name = "la_port"
    agency = "Port of LA"
    timezone = "America/Los_Angeles"
    start_urls = ["https://portofla.granicus.com/ViewPublisher.php?view_id=9"]

    def parse(self, response):
        items = response.xpath("//tbody/tr")
        items = items[0:30]
        for item in items:
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

    def _parse_start(self, item):
        """Calendar page does not have times.  Times can be found in agenda.
        Currently does not scrape time; defaults to 00:00
        """
        links = self._parse_links(item)
        if (len(links) > 0) and (links[0]["title"] == "Agenda"):
            url = links[0]["href"]
            print(url)
            rs = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response = html.fromstring(rs.content)

            try:
                items = response.xpath(
                    "//div[@id='contentBody']//div[@id='section-about']//strong"
                )
                starttime = items[2].text_content()
                return dateparse(starttime, fuzzy=True)
            except:
                items = response.xpath(
                    "//section[@class='cms-content text-info-block']"
                )
                starttime = items[0].text_content()
                sample_str = re.sub(r"\s+", "", starttime)
                try:
                    return dateparse(sample_str, fuzzy=True)
                except:
                    row = item.xpath("td[@class='listItem']/text()")
                    date = row[1].get()
                    return dateparse(date)

        row = item.xpath("td[@class='listItem']/text()")
        date = row[1].get()
        return dateparse(date)

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

    def _parse_location(self, item):
        """The location can be found in the agenda, not scraped yet"""

        links = self._parse_links(item)
        if (len(links) > 0) and (links[0]["title"] == "Agenda"):
            url = links[0]["href"]
            rs = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response = html.fromstring(rs.content)
            items = response.xpath(
                "//div[@id='contentBody']//div[@id='section-about']//strong"
            )
            location = items[0].text_content()
            clean_location = re.sub("\r\n", "\n", location)
            clean_location = re.sub("\xa0", " ", clean_location)

            end = clean_location.find("\n")
            name = (clean_location[:end]).strip()
            address = (clean_location[end:]).strip()

            return {"name": name, "address": address}

        return None

    def _parse_source(self, response):
        return response.url
