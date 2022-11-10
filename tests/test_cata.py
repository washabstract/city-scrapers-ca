from datetime import datetime
from os.path import dirname, join

# import pytest
from city_scrapers_core.constants import COMMISSION, ADVISORY_COMMITTEE, NOT_CLASSIFIED, TENTATIVE
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

# print(test_response2)
spider = CataSpider()

freezer = freeze_time("2022-09-22")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_items_c = [item for item in spider.parse(test_response_c)]
parsed_items_th = [item for item in spider.parse(test_response_th)]
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


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items_c[0]["description"] == "9:30AM - Via Webinar"
    assert parsed_items_th[1]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 10, 12, 0, 0)
    assert parsed_items_c[0]["start"] == datetime(2022, 2, 25, 9, 30)
    assert parsed_items_th[1]["start"] == datetime(2022, 9, 21, 13, 00)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 10, 13, 23, 59)
    assert parsed_items_c[0]["end"] == None
    assert parsed_items_th[1]["end"] == datetime(2022, 9, 22, 23, 59)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items_c[0]["time_notes"] == ""
    assert parsed_items_th[1]["time_notes"] == ""


# def test_id():
#     assert parsed_items[0]["id"] == 
# "cata/202210120000/x/california_transportation_commission_meeting"


# def test_status():
#     assert parsed_items[0]["status"] == TENTATIVE


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

def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
    assert parsed_items_c[0]["classification"] == ADVISORY_COMMITTEE
    assert parsed_items_th[1]["classification"] == NOT_CLASSIFIED

def test_all_day():
    assert parsed_items[0]["all_day"] is True
    assert parsed_items_c[0]["all_day"] is False
    assert parsed_items_th[1]["all_day"] is True