from datetime import datetime
from os.path import dirname, join

# import pytest
from city_scrapers_core.constants import (
    COMMISSION, ADVISORY_COMMITTEE, NOT_CLASSIFIED, TENTATIVE, PASSED
    )
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cata import CataSpider

test_response = file_response(
    join(dirname(__file__), "files", "cata.html"),
    url="https://catc.ca.gov/meetings-events/commission-meetings",
)
test_response_c = file_response(
    join(dirname(__file__), "files", "cata_committee.html"),
    url="https://catc.ca.gov/meetings-events/committee-meetings",
)
test_response_th = file_response(
    join(dirname(__file__), "files", "cata_town_hall.html"),
    url="https://catc.ca.gov/meetings-events/town-hall-meetings",
)
test_response_ts = file_response(
    join(dirname(__file__), "files", "cata_tri_state.html"),
    url="https://catc.ca.gov/meetings-events/tri-state-meetings",
)
test_response_ear = file_response(
    join(dirname(__file__), "files", "cata_equity_advisory_roundtable.html"),
    url="https://catc.ca.gov/meetings-events/equity-advisory-roundtable-meeting",
)

# print(test_response2)
spider = CataSpider()

freezer = freeze_time("2022-09-22")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_items_c = [item for item in spider.parse(test_response_c)]
parsed_items_th = [item for item in spider.parse(test_response_th)]
parsed_items_ts = [item for item in spider.parse(test_response_ts)]
parsed_items_ear = [item for item in spider.parse(test_response_ear)]

# print(len(parsed_items2))
# parsed_items = parsed_items + parsed_items2

freezer.stop()

# print(len(parsed_items))

def test_title():
    assert parsed_items[0]["title"] == "California Transportation Commission Meeting"
    assert(
        parsed_items_c[0]["title"] == "Road Charge Technical Advisory Committee Meeting"
    )
    assert parsed_items_th[1]["title"] == "Town Hall Meeting"
    assert parsed_items_ts[0]["title"] == "Tri-State Commission Meeting"
    assert parsed_items_ear[0]["title"] == "Equity Advisory Roundtable Meeting #5"



def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items_c[0]["description"] == "9:30AM - Via Webinar"
    assert parsed_items_th[1]["description"] == ""
    assert parsed_items_ts[0]["description"] == ""
    assert parsed_items_ear[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 10, 12, 0, 0)
    assert parsed_items_c[0]["start"] == datetime(2022, 2, 25, 9, 30)
    assert parsed_items_th[1]["start"] == datetime(2022, 9, 21, 13, 00)
    assert parsed_items_ts[0]["start"] == datetime(2019, 9, 16, 0, 0)
    assert parsed_items_ear[0]["start"] == datetime(2022, 2, 3, 0, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 10, 13, 23, 59)
    assert parsed_items_c[0]["end"] == None
    assert parsed_items_th[1]["end"] == datetime(2022, 9, 22, 23, 59)
    assert parsed_items_ts[0]["end"] == datetime(2019, 9, 17, 23, 59)
    assert parsed_items_ear[0]["end"] == None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items_c[0]["time_notes"] == ""
    assert parsed_items_th[1]["time_notes"] == ""
    assert parsed_items_ts[0]["time_notes"] == ""
    assert parsed_items_ear[0]["time_notes"] == ""


def test_id():
    assert(parsed_items[0]["id"] ==
    "cata/202210120000/x/california_transportation_commission_meeting")
    assert(parsed_items_c[0]["id"] ==
    "cata/202202250930/x/road_charge_technical_advisory_committee_meeting")
    assert parsed_items_th[1]["id"] == "cata/202209211300/x/town_hall_meeting"
    assert(parsed_items_ts[0]["id"] == 
    "cata/201909160000/x/tri_state_commission_meeting")
    assert(parsed_items_ear[0]["id"] ==
    "cata/202202030000/x/equity_advisory_roundtable_meeting_5")


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items_c[0]["status"] == PASSED
    assert parsed_items_th[1]["status"] == PASSED
    assert parsed_items_ts[0]["status"] == PASSED
    assert parsed_items_ear[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Santa Barbara - Cabrillo Pavilion",
        "address": ""
    }
    assert parsed_items_c[0]["location"] == {'address': '', 'name': ''}
    assert parsed_items_th[1]["location"] == {
        "name": "Lake Tahoe Community College - Boardroom",
        "address": ""
    }
    assert parsed_items_th[2]["location"] == {
        "name": "Butte County Association of Governments",
        "address": "Board Chambers\n"
        "326 Huss Drive, Suite 100\n"
        "Chico CA 95928"
    }
    assert  parsed_items_ts[0]["location"] == {
        "name": "",
        "address": "Skamania Lodge\n"
        "1131 Skamania Lodge Drive\n"
        "Stevenson, WA 98648"
    }
    assert parsed_items_ear[0]["location"] == {
        "name": "Via Webinar",
        "address": ""
    }
    assert parsed_items_ear[1]["location"] == {
        "name": "Sacramento and via Webinar",
        "address": "Department of Transportation\n"
        "Director's Basement Boardroom\n"
        "1120 N Street, Sacramento, CA 95814"
    }


def test_source():
    assert(
        parsed_items[0]["source"] == 
        "https://catc.ca.gov/meetings-events/commission-meetings"
    )
    assert(
        parsed_items_c[0]["source"] == 
        "https://catc.ca.gov/meetings-events/committee-meetings"
    )
    assert(
        parsed_items_th[1]["source"] == 
        "https://catc.ca.gov/meetings-events/town-hall-meetings"
    )
    assert(
        parsed_items_ts[0]["source"] == 
        "https://catc.ca.gov/meetings-events/tri-state-meetings"
    )
    assert(
        parsed_items_ear[0]["source"] == 
        "https://catc.ca.gov/meetings-events/equity-advisory-roundtable-meeting"
    )


def test_links():
    assert parsed_items[0]["links"] == [{
        'href': 'https://catc.ca.gov/meetings-events/commission-meetings/10-12-13-22',
        'title': 'View/Download October 12th - 13th Meeting Materials'}]
    assert parsed_items[2]["links"] == [
        {
            "href":"https://catc.ca.gov/-/media/ctc-media/documents/ctc-meetings"
            "/2022/2022-01/000-eta.pdf",
            "title": "1/26-27: Meeting Agenda (PDF)"
        },
        {
            "href": "https://platform.verbit.co/live_jobs"
            "/19362334-8bc0-4a2d-9766-e2e76a4b527d/attendee",
            "title": "1/26: Live Closed Captions"
        },
        {
            "href": "https://platform.verbit.co/live_jobs"
            "/4ecf728d-a7d8-45f5-9a48-6dae24fb5319/attendee",
            "title": "1/27: Live Closed Captions"
        },
        {
            "href": "https://catc.ca.gov/meetings-events/"
            "commission-meetings/01-26-27-22",
            "title": "View/Download January 26th - 27th Meeting Materials"
        },
    ]
    assert parsed_items_c[0]["links"] == [
        {
            "href":"https://catc.ca.gov/-/media/ctc-media/documents/programs/"
            "road-charge-technical-advisory-committee-meeting/"
            "2022/feb-25-2022/00-agenda2-a11y.pdf",
            "title": "2/25: Agenda"
        },
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/programs/"
            "road-charge-technical-advisory-committee-meeting/"
            "2022/feb-25-2022/00-agenda2-spanish-a11y.pdf",
            "title": "2/25: Agenda en Español"
        },
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/programs/"
            "road-charge-technical-advisory-committee-meeting/"
            "2022/feb-25-2022/tab-5-new-a11y.pdf",
            "title": "Tab 5 Revised"
        },
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/programs/"
            "road-charge-technical-advisory-committee-meeting/"
            "2022/feb-25-2022/tab-6-pres-a11y.pdf",
            "title": "Tab 6 Presentation"
        },
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/programs/"
            "road-charge-technical-advisory-committee-meeting/"
            "2022/feb-25-2022/tab-7-pres-a11y.pdf",
            "title": "Tab 7 Presentation"
        },
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/programs/"
            "road-charge-technical-advisory-committee-meeting/"
            "2022/feb-25-2022/tab-8-pres-a11y.pdf",
            "title": "Tab 8  Presentation"
        },
    ]
    assert parsed_items_th[1]["links"] == [
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/ctc-meetings/"
            "town-halls/092122-tahoe-townhall-a11y.pdf",
            "title": "9/21-22: Town Hall Agenda (pdf)"
        },
        {
            "href": "https://attendee.gotowebinar.com/register/2078228035478668812",
            "title": "9/21: Join the Webinar Remotely"
        },
        ]
    assert parsed_items_ts[0]["links"] == [
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/ctc-meetings/"
            "2019/20191209-final-stevenson-agenda-a11y.pdf",
            "title": "Agenda"
        },
        {
            "href": "https://wstc.wa.gov/agendas/2019/09/16/"
            "joint-meeting-agenda-september-16-17-2019/",
            "title": "Agenda with links to presentations"
        },
        {
            "href": "https://hostedevents.invintus.com/WATransportationCmsn/"
            "channel.html?clientID=6541166213&id=247&listingPage=1&"
            "listingSortBy=ascending&listingStart=2019-06-11&listingStop=2020-03-11",
            "title": "View Webcast Recordings"
        }
    ]
    assert parsed_items_ear[0]["links"] == [
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/ctc-meetings/"
            "2022/2022-02/ear-meeting/020322-roundtable-agenda-a11y.pdf",
            "title": "02/03: Agenda (PDF)"
        },
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/programs/"
            "equity-public-engagement/equity-advisory-roundtable/"
            "020322-roundtable-agenda-spanish-a11y.pdf",
            "title": "02/03: Agenda en Español (PDF)"
        },
        {
            "href": "https://platform.verbit.co/live_jobs/"
            "6e56c0be-aeac-4029-a278-4e5461823da6/attendee",
            "title": "02/03: Live Closed Captions"
        },
        {
            "href": "https://catc.ca.gov-/media/e85a2275a1d34d9284b8d2f4d4b3700b.ashx",
            "title": "02/03: Tab 4 Presentation"
        },
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/ctc-meetings/"
            "2022/2022-02/ear-meeting/tab-5-pres-a11y.pdf",
            "title": "02/03: Tab 5 Presentation"
        },
        {
            "href": "https://catc.ca.gov/-/media/ctc-media/documents/ctc-meetings/"
            "2022/2022-02/ear-meeting/tab-6-pres-a11y.pdf",
            "title": "02/03: Tab 6 Presentation"
        },
        {
            "href": "https://youtu.be/8jMOVgdwx6A",
            "title": "02/03: Webcast Recording Part 1"
        },
        {
            "href": "https://youtu.be/dl4aJpAo-dw",
            "title": "02/03: Webcast Recording Part 2"
        }
    ]

def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
    assert parsed_items_c[0]["classification"] == ADVISORY_COMMITTEE
    assert parsed_items_th[1]["classification"] == NOT_CLASSIFIED
    assert parsed_items_ts[0]["classification"] == COMMISSION
    assert parsed_items_ear[0]["classification"] == NOT_CLASSIFIED

def test_all_day():
    assert parsed_items[0]["all_day"] is True
    assert parsed_items_c[0]["all_day"] is False
    assert parsed_items_th[1]["all_day"] is True
    assert parsed_items_ts[0]["all_day"] is True
    assert parsed_items_ear[0]["all_day"] is False