import re
from datetime import datetime

from city_scrapers_core.constants import CLASSIFICATIONS, NOT_CLASSIFIED
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import ParserError
from dateutil.parser import parse as dateparse

from city_scrapers.items import Meeting


def create_meeting(self, response, item, head):
    meeting = Meeting(
        title=self._parse_title(item, response),
        description=self._parse_description(item, response),
        time_notes=self._parse_time_notes(item),
        links=self._parse_links(item, response),
        source=self._parse_source(response),
        created=datetime.now(),
        updated=datetime.now(),
    )

    (
        meeting["start"],
        meeting["end"],
        meeting["all_day"],
    ) = self._parse_start_end_all_day(item, head, response)

    meeting["location"] = self._parse_location(item, head, response)
    meeting["classification"] = self._parse_classification(meeting["title"])

    if meeting["start"] is None:
        return

    meeting["status"] = self._get_status(meeting)
    meeting["id"] = self._get_id(meeting)

    return meeting


class CatcSpider(CityScrapersSpider):
    name = "catc"
    agency = "California Transportation Commission"
    timezone = "America/Los_Angeles"
    start_urls = [
        "https://catc.ca.gov/meetings-events/commission-meetings",
        "https://catc.ca.gov/meetings-events/committee-meetings",
        "https://catc.ca.gov/meetings-events/equity-advisory-roundtable-meeting",
        "https://catc.ca.gov/meetings-events/joint-carb-meetings",
        "https://catc.ca.gov/meetings-events/town-hall-meetings",
        "https://catc.ca.gov/meetings-events/tri-state-meetings",
        "https://catc.ca.gov/meetings-events/workshops",
    ]

    def parse(self, response):
        # Equity Advisory Roundtable and Joint CARB Meetings
        if "equity-advisory-roundtable" in response.url or "joint-carb" in response.url:
            # extract all text and href element by element and store in a dict list
            items = []
            potential = []
            if "equity-advisory-roundtable" in response.url:
                sections = response.xpath("//main[@class='main-primary']//section")
                if len(sections) >= 3:
                    potential = sections[2].xpath("descendant::*")
            if "joint" in response.url:
                potential = response.xpath(
                    "//main[@class='main-primary']/div/h2[2]/"
                    "following-sibling::*/descendant-or-self::*"
                )

            for row in potential:
                text = row.xpath("text()").getall()
                text = "".join(text)
                if (
                    text
                    and text.strip() != ""
                    and not (
                        text.strip().startswith("(") and text.strip().endswith(")")
                    )
                ):
                    # add it to the list of items
                    href = row.xpath("@href").get()
                    text = text.replace("\xa0", " ")
                    text = text.strip()
                    items.append({"text": text, "href": href})

            # From items list, create a dict list list
            #   ie a list of meetings, where each meeting is a list of dictionaries
            newitems = []
            count = -1
            for row in items:
                is_title = False
                if "equity-advisory-roundtable" in response.url:
                    is_title = "Equity Advisory Roundtable Meeting" in row["text"]
                if "joint-carb" in response.url:
                    is_title = re.search(
                        r"\w+\s\d{1,2}\([A-Za-z]{1,2}\),\s\d{4}", row["text"]
                    )

                if is_title:
                    newitems.append([row])
                    count += 1
                else:
                    if count >= 0:
                        newitems[count].append(row)

            for item in newitems:
                head = item[0]["text"]
                meeting = create_meeting(self, response, item, head)
                yield meeting

        # Commission, Committee, Town Hall, Tri-State, and Workshop Meetings
        else:
            hr = "//main[@class='main-primary']/descendant::hr/following-sibling::h3|"
            h2 = "//main[@class='main-primary']/descendant::h2/following-sibling::h3|"
            sect = "//main[@class='main-primary']/descendant::section/h3|"
            h1 = "//main[@class='main-primary']/descendant::h1/following-sibling::h3|"
            ul = "//main[@class='main-primary']/descendant::ul/following-sibling::h3"
            path = hr + h2 + sect + h1 + ul
            meetings_raw = response.xpath(path)

            # Create my own `item` since all elements in a meeting are siblings
            #   (ie no hierarchy)
            # type(item) = selector list
            for first in meetings_raw:
                siblings = first.xpath("following-sibling::*")
                i = 0
                item = [first]
                num_sibs = len(siblings)
                while i < num_sibs and "<h3>" not in siblings[i].get():
                    item.append(siblings[i])
                    i += 1
                    if "workshops" in response.url and "<ul>" in siblings[i].get():
                        num_sibs = i + 1

                h = item[0].xpath(".//text()")
                head = h.get().strip() if h else ""

                meeting = create_meeting(self, response, item, head)
                yield meeting

    def _parse_title(self, item, response):
        clean_title = ""

        # Commission Meetings
        if "commission-meetings" in response.url:
            title = item[0].xpath("text()")
            if title:
                title = title.get().strip()
                clean_title = title.split(":")[0]

        # Equity Advisory Roundtable Meetings
        elif "equity-advisory-roundtable" in response.url:
            clean_title = item[0]["text"]

        # Joint CARB Meetings
        elif "joint" in response.url:
            if len(item) > 1:
                clean_title = item[1]["text"]

        # Committee, Town Hall, Tri-State, and Workshops
        else:
            # <h4> marks the title
            items = item
            for item in items:
                if "<h4>" in item.get():
                    title = item.xpath(".//text()").getall()
                    if len(title) > 0:
                        if "town-hall-" in response.url:
                            t = title[0]
                            title = t.split("-")
                        clean_title = title[0].strip()
                        break

        return clean_title

    def _parse_description(self, item, response):
        if "committee-meetings" in response.url:
            items = item[2 : len(item) - 1]
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

        # Committee and Workshops
        if "committee-meetings" in response.url or "workshops" in response.url:
            # Date: in the h2
            # Time: have to search the full text for that meeting/item
            title_segs = item[0].xpath(".//text()").getall()
            title = "".join(title_segs)

            body = ""
            items = item
            for item in items:
                row = "".join(item.xpath(".//text()").getall())
                body += row

            enddt = ""
            startdt = ""
            times = re.findall(r"\d{1,2}:\d\d\s?[aApP][mM]", body)
            if len(times) > 0:
                startdt = title + " " + times[0]
            if len(times) > 1:
                enddt = title + " " + times[1]

            try:
                start = dateparse(startdt, fuzzy="True", ignoretz="True")
            except ParserError:
                start = None

            try:
                end = dateparse(enddt, fuzzy="True", ignoretz="True")
            except ParserError:
                end = None

        # Equity Advisory Roundtable Meetings
        elif "equity-advisory-roundtable" in response.url:
            if len(item) > 1:
                dt = item[1]["text"].split("-")[0]
                try:
                    start = dateparse(dt, fuzzy="True", ignoretz="True")
                except ParserError:
                    start = None

        # Joint CARB Meetings
        elif "joint-carb" in response.url:
            date = ""
            start_time = ""
            end_time = ""
            if len(item) > 0:
                date = item[0]["text"]
            if len(item) > 3:
                time = item[2]["text"]
                times = time.split("-")
                start_time = times[0]
                if len(times) > 1:
                    end_time = times[1]

            try:
                start = dateparse(
                    date + " " + start_time, fuzzy="True", ignoretz="True"
                )
            except ParserError:
                start = None

            if end_time != "":
                try:
                    end = dateparse(
                        date + " " + end_time, fuzzy="True", ignoretz="True"
                    )
                except ParserError:
                    end = None

        # Commission, Town Hall, and Tri-State Meetings
        else:
            # Find date, example format: October 12(W) - 13(TH), 2022
            # If date is a range, mark all_day=True and parse using only the start date
            # Remove the (w) weekday marker for dateparsing
            dt = re.findall(
                r"(\w+\s\d{1,2}\([A-Za-z]{1,2}\)(\s?[-&]\s?\d{1,2}\([A-Za-z]{1,2}\))?,\s\d{4})",  # NOQA
                title,
            )
            if len(dt) > 0 and len(dt[0]) > 0:
                dt1 = re.findall(r"\s?[-&]\s?\d{1,2}\([A-Za-z]{1,2}\)", dt[0][0])
                if len(dt1) > 0:
                    # Multi-day event
                    clean_dt = re.sub(
                        r"\([A-Za-z]{1,2}\)\s?[-&]\s?\d{1,2}\([A-Za-z]{1,2}\)",
                        "",
                        dt[0][0],
                    )
                    end_dt = re.sub(r"\s?\d{1,2}\([A-Za-z]{1,2}\)\s?[-&]", "", dt[0][0])
                    clean_end_dt = re.sub(r"\([A-Za-z]{1,2}\)", "", end_dt)
                    all_day = True

                    # Set end date if there is
                    # End time of all day event is at 11:59 on the last day
                    try:
                        end_str = clean_end_dt + " 11:59PM"
                        end = dateparse(end_str, fuzzy="True", ignoretz="True")
                    except ParserError:
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
                    start = dateparse(clean_dt, fuzzy="True", ignoretz="True")
                except ParserError:
                    start = None

        return start, end, all_day

    def _parse_time_notes(self, item):
        return ""

    def _parse_location(self, item, title, response):
        address = ""
        name = ""

        # Equity Advisory Roundtable Meeting
        if "equity-advisory-roundtable" in response.url:
            if len(item) > 1:
                title = item[1]["text"]
                title_segs = title.split("-")
                if len(title_segs) > 1:
                    name = title_segs[1].strip()

            if len(item) > 2:
                for row in item[2:]:
                    txt = row["text"].replace("\xa0", " ").strip()
                    if row["href"] or (txt.startswith("(") and txt.endswith(")")):
                        break
                    address = address + txt + "\n"
            address = address.strip()

        # Joint CARB Meeting
        elif "joint" in response.url:
            count = -1
            for row in item:
                if row["href"] is not None:
                    break
                count += 1

            if count > 1:
                address = item[count]["text"]

        # Town Hall Meetings
        elif "town-hall-" in response.url:
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
                # get paragraph
                for item in items:
                    if "<p>" in item.get():
                        location = item.xpath("text()").getall()
                        if len(location) > 0:
                            name = location[0].strip()
                            address = ("".join(location[1:])).strip()

        # Tri-State Meeting
        elif "tri-state-" in response.url:
            items = item
            for item in items:
                if "<div>" in item.get():
                    location = item.xpath(".//text()").get()
                    if location:
                        address = address + location.strip() + "\n"
            address = address.strip()

        # Workshops
        elif "workshop" in response.url:
            if len(item) > 3 and "<ul>" not in item[3].get():
                name = item[3].xpath("text()").get().strip()

            if len(item) > 4:
                for row in item[4:]:
                    if "<ul>" in row.get():
                        break
                    address = address + row.xpath("text()").get().strip() + "\n"
                address = address.strip()

        # Commission and Committee Meetings
        else:
            split_title = re.split(r",\s?\d{4}\s?-", title)
            if len(split_title) > 1:
                name = split_title[1].strip()

        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item, response):
        links = []

        # Equity Advisory Roundtable and Joint CARB Meetings
        if "equity-advisory-roundtable" in response.url or "joint" in response.url:
            for row in item:
                if row["href"]:
                    href = row["href"]
                    if href.find("https://") == -1:
                        href = "https://catc.ca.gov" + href
                    title = row["text"].replace("\xa0", " ").strip()
                    links.append({"href": href, "title": title})

        # Commission, Committee, Town Hall, Tri-State, Workshops
        else:
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
        return response.url