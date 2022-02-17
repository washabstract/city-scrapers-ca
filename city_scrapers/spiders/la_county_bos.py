import re
from datetime import datetime
from urllib.parse import urljoin

from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class LaCountyBosSpider(CityScrapersSpider):
    name = "la_county_bos"
    agency = "LA County Board of Supervisors"
    timezone = "America/Los_Angeles"
    start_urls = ["http://bos.lacounty.gov/Board-Meeting/Board-Agendas"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        sections = self._parse_sections(response)
        for item in sections:
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

    def _parse_sections(self, response):
        sections = response.css(".price_border")
        items = []
        while len(sections) > 1:
            section = sections.pop(0)
            agenda_text = " ".join(
                [text.strip() for text in section.css("li::text").getall()]
            )
            agenda_re = re.search(r"Agenda for the (.+) of (.+\.)", agenda_text)
            matched = False
            for i in range(1, len(sections)):
                match_text = " ".join(
                    [text.strip() for text in sections[i].css("li::text").getall()]
                )
                match_re = re.search(r"Agenda for the (.+) of (.+\.)", match_text)
                if (agenda_re.group(1) == match_re.group(1)) and (
                    agenda_re.group(2) == match_re.group(2)
                ):
                    supp_agenda = sections.pop(i)
                    items.append((section, supp_agenda))
                    matched = True
                    break
            if not matched and "Supplemental" in agenda_text:
                self.logger.info("Could not find match for %s", section)
            elif not matched:
                items.append((section, None))
        return items

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        item = item[0]
        m = re.search("Agenda for the (.+) of", item.css("li::text").get())
        return m.group(1)

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        agenda = urljoin(self.start_urls[0], item[0].css("a::attr('href')").get())
        if item[1]:
            supplemental_agenda = urljoin(
                self.start_urls[0], item[1].css("a::attr('href')").get()
            )
            return (
                f"Meeting Agenda: {agenda}\nSupplemental Agenda: {supplemental_agenda}"
            )
        return f"Meeting Agenda: {agenda}"

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        item = item[0]
        agenda_text = " ".join([text.strip() for text in item.css("li::text").getall()])
        m = re.search(r"of (.+\.)", agenda_text)
        return dateparse(m.group(1))

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
            "address": "500 West Temple Street, Los Angeles, California 90012",
            "name": "Kenneth Hahn Hall of Administration",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = [
            {
                "href": urljoin(
                    self.start_urls[0], item[0].css("a::attr('href')").get()
                ),
                "title": "Meeting/Agenda Information",
            }
        ]
        if item[1]:
            links.append(
                {
                    "href": urljoin(
                        self.start_urls[0], item[1].css("a::attr('href')").get()
                    ),
                    "title": "Supplemental Agenda",
                }
            )
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
