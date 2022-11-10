from datetime import datetime
from logging.handlers import SMTPHandler
import re
from tokenize import Special

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse


class CataSpider(CityScrapersSpider):
    name = "cata"
    agency = "California Transportation Commission"
    timezone = "America/Los_Angeles"
    start_urls = [
        "https://catc.ca.gov/meetings-events/commission-meetings",
        "https://catc.ca.gov/meetings-events/committee-meetings",
        "https://catc.ca.gov/meetings-events/town-hall-meetings"]

    def parse(self, response):
        meetings_raw = response.xpath("//div[@id='main-content']/descendant::hr/following-sibling::h3|//div[@id='main-content']/descendant::h2/following-sibling::h3|//div[@id='main-content']/descendant::section/h3")
        # if "committee-meetings" in response.url:
        #     h2_raw = response.xpath("//div[@id='main-content']/descendant::h2/following-sibling::h3")
        #     meetings_raw = meetings_raw + h2_raw
        for first in meetings_raw:
            siblings = first.xpath("following-sibling::*")
            i = 0
            item = [first]
            num_sibs = len(siblings)
            while i < num_sibs and siblings[i].get() != "<hr>":
                item.append(siblings[i])
                i+=1

            # print(len(item))
            meeting = Meeting(
                title=self._parse_title(item, response),
                description=self._parse_description(item, response),
                # classification=self._parse_classification(item),
                # start=self._parse_start(item),
                # end=self._parse_end(item),
                # all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                # location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
                created=datetime.now(),
                updated=datetime.now(),
            )

            # use the heading(the title) to get time and location
            h = item[0].xpath("text()")
            head = h.get().strip() if h else ""
            # if "town-hall-meetings" in response.url:
            #     print(head)
            meeting["start"], meeting["end"], meeting["all_day"] = self._parse_start_end_all_day(item, head, response)
            meeting["location"] = self._parse_location(item, head, response)

            meeting["classification"] = self._parse_classification(meeting["title"])

            # if meeting["start"] is None:
            #     print("bap!")
            #     return

            # meeting["status"] = self._get_status(meeting)
            # meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item, response):
        if "committee-meetings" in response.url or "town-hall-" in response.url:
            # For committee and town hall meetings: <h4> is the title
            items = item
            for item in items:
                if "<h4>" in item.get():
                    title = item.xpath("text()").getall()
                    if len(title) > 0:
                        if "town-hall-" in response.url:
                            t = title[0]
                            title = t.split("-")
                            print(title)
                        return title[0].strip()
        else:
            title = item[0].xpath("text()")
            if title:
                title = title.get().strip()
                return title.split(":")[0]
        return ""

    def _parse_description(self, item, response):
        """Parse or generate meeting description."""
        if "committee-meetings" in response.url:
            items = item[2:len(item) - 1]
            text = ""
            for item in items:
                t = "".join(item.xpath("text()").getall())
                text = text + "\n" + t.strip()
            return text.strip()
        return ""

    def _parse_classification(self, title):
        for classification in CLASSIFICATIONS:
            if classification.lower() in title.lower():
                return classification
        return NOT_CLASSIFIED

    def _parse_start_end_all_day(self, item, title, response):
        start = None
        end = None
        all_day = False
        
        # Committee meeting date and time
        # Date is in the h2
        # Time: have to search the full text for that meeting/item
        if "committee-meetings" in response.url:
            title_segs = item[0].xpath(".//text()").getall()
            title = "".join(title_segs)
            
            body = ""
            items = item
            for item in items:
                row = "".join(item.xpath(".//text()").getall())
                body += row
            
            times = re.findall(r"\d{1,2}:\d\d\s?[aApP][mM]", body)
            if len(times) > 0:
                title = title + " " + times[0]
                # print(title)

            try:
                start = dateparse(title, fuzzy = "True", ignoretz = "True")
            except ParserError:
                start = None
            return start, end, all_day
        
        # Find date, example format: October 12(W) - 13(TH), 2022
        # If date is a range, mark all_day=True and parse using only the start date
        # Remove the (w) weekday marker for dateparsing
        dt = re.findall(
            r"(\w+\s\d{1,2}\([A-Za-z]{1,2}\)(\s?[-&]\s?\d{1,2}\([A-Za-z]{1,2}\))?,\s\d{4})", title)
        if len(dt) > 0 and len(dt[0]) > 0:
            if "town-hall-" in response.url:
                print(dt[0][0])
            dt1 = re.findall(r"\s?[-&]\s?\d{1,2}\([A-Za-z]{1,2}\)", dt[0][0])
            if len(dt1) > 0:
                # Multi-day event
                clean_dt = re.sub(
                    r"\([A-Za-z]{1,2}\)\s?[-&]\s?\d{1,2}\([A-Za-z]{1,2}\)", "", dt[0][0])
                end_dt = re.sub(
                    r"\s?\d{1,2}\([A-Za-z]{1,2}\)\s?[-&]", "", dt[0][0])
                clean_end_dt = re.sub(r"\([A-Za-z]{1,2}\)", "", end_dt)
                all_day = True
                
                # Set end date if there is
                # End time of all day event is at 11:59 on the last day
                try: 
                    end_str = clean_end_dt + " 11:59PM"
                    end = dateparse(end_str, fuzzy = "True", ignoretz = "True")
                except:
                    end = None
            
            else:
                # Single day event
                clean_dt = re.sub(r"\([A-Z]{1,2}\)", "", dt[0][0])
            
            # search body for time
            body = ""
            items = item
            for item in items:
                row = "".join(item.xpath(".//text()").getall())
                body += row
            
            times = re.findall(r"\d{1,2}:\d\d\s?[aApP][mM]", body)
            if len(times) > 0:
                clean_dt = clean_dt + " " + times[0]

            try:
                start = dateparse(clean_dt, fuzzy = "True", ignoretz = "True")
            except ParserError:
                start = None

        return start, end, all_day

    def _parse_time_notes(self, item):
        return ""

    def _parse_location(self, item, title, response):
        address = ""
        name = ""

        # Town Hall Meetings
        if "town-hall-" in response.url:
            t = ""
            items = item
            for item in items:
                if "<h4>" in item.get():
                    title = item.xpath("text()").getall()
                    if len(title) > 0:
                        t = title[0].strip()
            
            title_segs = t.split("-")
            if len(title_segs) > 1:
                name = ("-".join(title_segs[1:])).strip()
            else:
                #get paragraph
                for item in items:
                    if "<p>" in item.get():
                        location = item.xpath("text()").getall()
                        if len(location) > 0:
                            name = location[0].strip()
                            address = ("".join(location[1:])).strip()
        
        # Comission Meetings
        else:
            split_title = re.split(r",\s?\d{4}\s?-", title)
            if len(split_title) > 1:
                name = split_title[1].strip()
        
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item):
        links = []

        # collect every link at any sublevel of each "row" in the item
        for row in item:
            r = row.xpath(".//a")
            for link in r:
                # get the title and link, with error handling
                
                title = link.xpath("text()").get()
                if title:
                    title = re.sub("\xa0", " ", title)
                    title = title.strip()
                else:
                    title = ""
                
                try:
                    href = link.xpath("@href").get().strip()
                except AttributeError:
                    href = ""

                # if it doesnt have https://, start with https://catc.ca.gov
                if href != "" and href.find("https://") == -1:
                    href = "https://catc.ca.gov" + href

                links.append({"href": href, "title": title})
            
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url



'''
NOTES
- finished committee meetings
- sort of.  all the mid-text is put into description
- did not bother trying to parse location
    - might be able to easily parse "via webinar"

Next:
Equity Advisory Roundtable Meeting page
jk no this one is mean


'''