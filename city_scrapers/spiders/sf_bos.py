from datetime import datetime
from urllib.parse import urljoin

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as datetime_parse

from city_scrapers.items import Meeting


class SfBosSpider(CityScrapersSpider):
    name = "sf_bos"
    agency = "San Francisco Board of Supervisors"
    timezone = "America/Los_Angeles"
    start_urls = ["https://sfbos.org/events/calendar"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        meeting_table = response.css(".views-table tbody")
        default_address = response.css("footer div.sf311::text").get().strip()
        for item in meeting_table.css("tr"):
            meeting = Meeting(
                title=self._parse_title(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item, default_address),
                source=self._parse_source(response),
                created=datetime.now(),
                updated=datetime.now(),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield response.follow(
                item.css('td.views-field-title a::attr("href")').get(),
                callback=self._parse_event,
                cb_kwargs={"meeting": meeting, "item": item},
                dont_filter=True,
            )

    def _parse_event(self, response, meeting, item):
        """Parse or generate event contents from event yield."""
        event_contents = None
        if "files" in response.url:
            event_contents = response.url
            meeting["description"] = "More information: " + event_contents
        else:
            event_contents = response.css("article.node-event .content")
            meeting["description"] = event_contents.get()

        links = []
        if type(event_contents) is str:
            links.append(
                {"href": event_contents, "title": "Meeting/Agenda Information"}
            )
        else:
            for link in event_contents.css(".field-type-link-field"):
                new_link = {
                    "href": link.css('a::attr("href")').get(),
                    "title": link.css("div.field-label::text").get(),
                }
                if "additional information link" in new_link["title"].lower():
                    new_link["title"] = "Meeting/Agenda Information"
            for link in event_contents.css("div.calendar-links a"):
                links.append(
                    {
                        "href": urljoin(response.url, link.css('::attr("href")').get()),
                        "title": link.css("::text").get(),
                    }
                )
            links.append(
                {
                    "href": urljoin(
                        response.url,
                        item.css('td.views-field-title a::attr("href")').get(),
                    ),
                    "title": meeting["title"],
                }
            )

        meeting["links"] = links
        return meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css("td.views-field-title a::text").get()

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        for classification in CLASSIFICATIONS:
            if classification in item.css("td.views-field-title a::text").get():
                return classification
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return datetime_parse(item.css("span.date-display-single::text").get())

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item, default_address):
        """Parse or generate location."""
        loc_str = item.css("td.views-field-field-event-location-premise").get().strip()
        if "cancel" in loc_str.lower():
            return {
                "address": "",
                "name": "",
            }
        if "remote" in loc_str.lower():
            return {
                "address": "",
                "name": loc_str,
            }
        try:
            int(loc_str)
        except ValueError:
            return {
                "address": default_address.replace("Room 244", loc_str),
                "name": "SF BOS " + loc_str,
            }
        else:
            return {
                "address": default_address.replace("244", loc_str),
                "name": "SF City Hall Room " + loc_str,
            }

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
