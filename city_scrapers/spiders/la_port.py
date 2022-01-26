from urllib.parse import urljoin

from city_scrapers_core.constants import NOT_CLASSIFIED, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class LaPortSpider(CityScrapersSpider):
    name = "la_port"
    agency = "Port of LA"
    timezone = "America/Los_Angeles"
    start_urls = ["https://portofla.granicus.com/ViewPublisher.php?view_id=9"]

    # Not that important?? It's only useed in datetime
    def parse(self, response):
        for url in response.xpath("//a[text()='Agenda']/@href"):
            url = urljoin(response.url, url.extract())
            yield response.follow(url, callback=self.parse_meeting, dont_filter=True)

    def parse_meeting(self, response):
        print("parsing meeting")
        item = response.xpath("//div[@id='contentBody']")
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
        )

        meeting["status"] = TENTATIVE #self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, item):
        print(type(item))
        # about = item.xpath("//div[@id='section-about']")
        title = item.xpath("//div[@id='section-about']//strong")
        print(title[0].get())
        print(title[1].get())
        print(title[2].get())
        return title[1].get()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

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
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
