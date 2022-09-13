import re
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class MetrolinkSpider(CityScrapersSpider):
    name = "metrolink"
    agency = "Southern California Regional Rail Authority"
    timezone = "America/Chicago"
    start_urls = ["https://metrolink.granicus.com/ViewPublisher.php?view_id=8"]

    def parse(self, response):
        for item in response.xpath("//tr[@class='listingRow']"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
                created=datetime.now(),
                updated=datetime.now(),
            )
            meeting["classification"] = self._parse_classification(meeting["title"])
            meeting["start"] = self._parse_start(item, meeting["title"])

            if meeting["start"] is None:
                return

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        title = item.xpath("./td[@headers='Name']/text()")
        if len(title) < 1:
            return ""
        return " ".join([t.strip() for t in title.extract()]).strip()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, title):
        if "committee" in title.lower():
            return COMMITTEE
        return BOARD

    def _parse_start(self, item, title):
        date = item.xpath(".//td[contains(@headers, 'Date')]/text()").extract()
        if len(date) < 1:
            return None
        clean_date = re.sub("\xa0", " ", date[0]).strip()
        try:
            date = dateparse(clean_date, fuzzy=True, ignoretz=True)
            if date.hour == 0:
                time = ""
                yr = str(date.year)
                for key in default_times[yr]:
                    if key in title.lower():
                        time = default_times[yr][key]
                date = dateparse(clean_date + " " + time, fuzzy=True, ignoretz=True)
            return date
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
            "address": "900 Wilshire Blvd, Riverside Conference Room, 12th Floor, "
            "Los Angeles, CA 90017",
            "name": "Metrolink Headquarters Building",
        }

    def _parse_links(self, item):
        result = []
        links = item.xpath(".//a")
        if len(links) < 1:
            return result

        for link in links:
            href = link.xpath("./@href")
            if len(href) < 1:
                continue
            href = href[0].extract()

            title = link.xpath("./text()")
            if len(title) < 1:
                title = ""
            else:
                title = title[0].extract().strip()

            # If it has a clip_id, it's a good link
            if "id=" in href:
                result.append({"href": "https:" + href, "title": title})

            # If not, check for onclick, find the first argument
            else:
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

                    href = "https:" + text[beg:end]
                    result.append({"href": href, "title": title})

        return result

    def _parse_source(self, response):
        return response.url


default_times = {
    "2022": {"board": "9am", "audit": "9am", "executive": "10am", "safety": "11am"},
    "2021": {"board": "9am", "audit": "9am", "executive": "10am", "safety": "11am"},
    "2020": {
        "board": "10am",
        "audit": "10:30am",
        "executive": "9am",
        "safety": "9:30am",
    },
    "2019": {"board": "10am", "audit": "9am"},
    "2018": {"board": "10am", "audit": "9am"},
    "2017": {"board": "10am", "audit": "9am"},
    "2016": {"board": "10am", "audit": "9am"},
    "2015": {"board": "10am", "audit": "9am"},
    "2014": {
        "board": "10am",
        "audit": "10:30am",
        "legislative": "9am",
        "finance": "10am",
        "safety": "10am",
    },
    "2013": {
        "board": "10am",
        "audit": "10:30am",
        "legislative": "9am",
        "finance": "10am",
        "safety": "10am",
    },
    "2012": {
        "board": "10am",
        "audit": "10:30am",
        "legislative": "9am",
        "finance": "10am",
        "safety": "10am",
    },
    "2011": {
        "board": "10am",
        "audit": "10am",
        "legislative": "10am",
        "finance": "10am",
        "safety": "10am",
    },
    "2010": {"board": "9am"},
}
