import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class LadwpSpider(CityScrapersSpider):
    name = "ladwp"
    agency = "LA Department of Water and Power"
    timezone = "America/Los_Angeles"
    start_urls = ["http://ladwp.granicus.com/ViewPublisher.php?view_id=2"]

    def parse(self, response):
        for item in response.xpath("//tr[@class='listingRow']"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
                created=datetime.now(),
                updated=datetime.now(),
            )

            if meeting["start"] is None:
                return

            meeting["end"] = self._parse_end(item, meeting["start"])
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

    def _parse_classification(self, item):
        return BOARD

    def _parse_start(self, item):
        date = item.xpath(".//td[contains(@headers, 'Date')]/text()").extract()
        if len(date) < 1:
            return None
        clean_date = re.sub("\xa0", " ", date[0]).strip()
        try:
            date = dateparse(clean_date, fuzzy=True, ignoretz=True)
            if date.hour == 0:
                date = date.replace(hour=10, minute=0)
            return date
        except ParserError:
            return None

    def _parse_end(self, item, start):
        if start is None:
            return None

        time = item.xpath(".//td[contains(@headers, 'Duration')]/text()")
        if len(time) < 1:
            return None

        time = time[0].extract()
        time = re.sub("\xa0", " ", time)

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
                title = title[0].extract()

            # If it has a clip_id, it's a good link
            if "clip_id=" in href:
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

            # If THAT doesnt work, it's a bad link.  Skip.

        return result

    def _parse_source(self, response):
        return response.url
