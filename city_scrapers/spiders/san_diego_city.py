import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

from city_scrapers_core.constants import NOT_CLASSIFIED, CITY_COUNCIL
from city_scrapers.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

from dateutil.parser import parse



class SanDiegoCitySpider(CityScrapersSpider):
    name = "san_diego_city"
    agency = "San Diego"
    sub_agency = "City"
    timezone = "America/Los_Angeles"
    past_meeting_url = "https://sandiego.granicus.com/ViewPublisher.php?view_id=3"
    start_urls = [
        past_meeting_url, 
        # "https://sandiego.hylandcloud.com/211agendaonlinecouncil"
    ]

    def parse(self, response):
        if response.url == self.past_meeting_url:
            # past meetings
            for item in response.xpath(".//tbody/tr"):
                start = self._parse_start(item)
                meeting = Meeting(
                    title=self._parse_title(item),
                    description=self._parse_description(item),
                    classification=self._parse_classification(item),
                    start=start,
                    end=self._parse_end(item, start),
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
        else:
            # Upcoming
            pass

    def _parse_title(self, item):
        title = item.xpath(".//td[1]/text()").get()
        return title

    def _parse_description(self, item):
        "No description"
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return CITY_COUNCIL

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        start_date_str = item.xpath(".//td[2]/text()").get()
        start = parse(start_date_str)
        return start.replace(tzinfo=None)

    def _parse_end(self, item, start: datetime):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        meeting_length = item.xpath(".//td[3]/text()").get()

        match_regex = r"(?P<hours>\d+)\shr\s(?P<mins>\d+)\smin"
        hours_mins_match = re.search(match_regex, meeting_length)

        # Try to typecast
        if hours_mins_match:
            try:
                hours, mins = hours_mins_match.group("hours", "mins")
                hours = int(hours)
                mins = int(mins)
                delta = timedelta(hours=hours, minutes=mins)
                end = start + delta
                return end
            except:
                pass
            
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
            "address": "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101",
            "name": "City Administration Building",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        results = []

        video1 = item.xpath(".//td[4]/a/@onclick").get() # inside a window.open 
        minutes = item.xpath(".//td[5]/a/@href").get()
        audio = item.xpath(".//td[6]/a/@href").get()
        video2 = item.xpath(".//td[7]/a/@href").get()

        if video1 is not None:
            # Extracting the url from the onclick function
            url_match = r"'(?P<url>//.*?)'"
            video1 = re.search(url_match, video1)
            if video1:
                video1 = video1.group("url")
                results.append({
                    "title": "Video",
                    "href": urljoin("https:", video1)
                })
        
        if minutes is not None:
            results.append({
                "title": "Minutes",
                "href": urljoin("https:", minutes)
            })
        
        if audio is not None:
            results.append({
                "title": "Audio",
                "href": audio
            })

        if video2 is not None:
            results.append({
                "title": "Video",
                "href": video2 # No need for urljoin
            })

        return results

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
