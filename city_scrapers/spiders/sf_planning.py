from datetime import datetime
from urllib.parse import urljoin

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


class SfPlanningSpider(CityScrapersSpider):
    name = "sf_planning"
    agency = "SF Planning Commission"
    timezone = "America/Los_Angeles"
    start_urls = [
        "https://sfplanning.org/hearings-cpc-grid",
        "https://sfplanning.org/hearings-cpc-grid?keys=&"
        "field_events_timeframe_target_id=2&field_id_previous_years_mobile=All"
        "&field_id_upcoming_years_mobile=All&field_id_previous_years=All"
        "&field_id_upcoming_years=All",
    ]

    def parse(self, response):
        for url in response.xpath("//a[text()='Read More']/@href"):
            url = urljoin(response.url, url.extract())
            yield response.follow(url, callback=self.parse_meeting, dont_filter=True)

    def parse_meeting(self, response):
        item = response.xpath("//article/div")
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
        event_type = item.xpath('//div[@class="event-type"]/text()').extract()[0]
        return f"{event_type} for SF Planning Commission"

    def _parse_description(self, item):
        return item.xpath('//div[@class="body"]').extract()[0]

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.xpath('//h3[@class="date"]/text()').extract()[0]
        time = item.xpath('//div[@class="time"]/text()').extract()[1].strip()
        return dateparse(date + " " + time, fuzzy=True)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        time = item.xpath('//div[@class="time"]/text()').extract()[1].strip().lower()
        return "all day" in time

    def _parse_location(self, item):
        """Parse or generate location."""
        location = (
            item.xpath('//div[@class="location"]/text()')
            .extract()[1]
            .strip()
            .split("\n")
        )
        location[0] = location[0].strip()
        location[1] = location[1].strip()
        location = " ".join(location)
        return {
            "address": location,
            "name": "SF Planning Commission",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        if len(item.xpath('//a[text()="AGENDA"]/@href').extract()) > 0:
            links.append(
                {
                    "href": item.xpath('//a[text()="AGENDA"]/@href').extract()[0],
                    "title": "Meeting/Agenda Information",
                }
            )
        if len(item.xpath('//a[text()="SUPPORTING"]/@href').extract()) > 0:
            links.append(
                {
                    "href": item.xpath('//a[text()="SUPPORTING"]/@href').extract()[0],
                    "title": "Supporting Documents",
                }
            )
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
