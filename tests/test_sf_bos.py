from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMISSION, COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.sf_bos import SfBosSpider

test_response = file_response(
    join(dirname(__file__), "files", "sf_bos.html"),
    url="https://sfbos.org/events/calendar",
)
test_event_response = file_response(
    join(dirname(__file__), "files", "sf_bos_event.html"),
    url=(
        "https://sfbos.org/event/"
        "youth-commission-civic-engagement-committee-cancelled-12"
    ),
)

spider = SfBosSpider()


@pytest.fixture()
def parsed_items():
    freezer = freeze_time("2021-03-15")
    freezer.start()
    parsed_items = [
        (item.cb_kwargs["meeting"], item.cb_kwargs["item"])
        for item in spider.parse(test_response)
    ]
    freezer.stop()
    return parsed_items


@pytest.fixture()
def parsed_event(parsed_items):
    return spider._parse_event(
        test_event_response,
        parsed_items[0][0],
        parsed_items[0][1],
    )


def test_title(parsed_items):
    assert (
        parsed_items[0][0]["title"]
        == "Youth Commission - Civic Engagement Committee (Cancelled)"
    )


def test_start(parsed_items):
    assert parsed_items[0][0]["start"] == datetime(2021, 3, 22, 16, 30)


def test_end(parsed_items):
    assert parsed_items[0][0]["end"] is None


def test_time_notes(parsed_items):
    assert parsed_items[0][0]["time_notes"] == ""


def test_id(parsed_items):
    assert (
        parsed_items[0][0]["id"]
        == "sf_bos/202103221630/x/youth_commission_civic_engagement_committee_"
    )


def test_status(parsed_items):
    assert parsed_items[0][0]["status"] == "cancelled"


def test_location(parsed_items):
    assert parsed_items[0][0]["location"] == {
        "name": "",
        "address": "",
    }


def test_source(parsed_items):
    assert parsed_items[0][0]["source"] == "https://sfbos.org/events/calendar"


def test_classification(parsed_items):
    assert parsed_items[0][0]["classification"] == COMMISSION
    assert parsed_items[1][0]["classification"] == COMMISSION
    assert parsed_items[2][0]["classification"] == BOARD
    assert parsed_items[3][0]["classification"] == COMMITTEE


def test_all_day(parsed_items):
    assert parsed_items[0][0]["all_day"] is False


def test_description(parsed_event):
    with open("test.log", "a") as f:
        f.write(parsed_event["description"])
    assert parsed_event["description"] == (
        '<div class="content">\n    '
        '<div class="field field-name-field-event-date field-type-datetime '
        'field-label-inline clearfix">'
        '<div class="field-label">Date: </div>'
        '<div class="field-items" id="md1">'
        '<div class="field-item even">'
        '<span class="date-display-single" property="dc:date" datatype="xsd:dateTime"'
        ' content="2021-03-22T16:30:00-07:00">Monday, March 22, 2021 - 4:30pm</span>'
        "</div></div></div>"
        '<div class="calendar-links"><a href="/events/calendar">All Events</a>     '
        '<a href="/events/calendar/month/?field_event_category_tid=91">'
        "Youth Commission</a></div>"
        '<div class="field field-name-field-event-location field-type-addressfield '
        'field-label-above"><div class="field-label">Location: </div>'
        '<div class="field-items" id="md2"><div class="field-item even">'
        '<div class="street-block"><div class="premise">Cancelled</div></div>\n'
        '<span class="country">United States</span></div></div></div>'
        '<div class="field field-name-field-event-url field-type-link-field '
        'field-label-inline clearfix">'
        '<div class="field-label">Additional information link: </div>'
        '<div class="field-items" id="md3"><div class="field-item even">'
        '<a href="https://sfgov.org/youthcommission//event/2021/CE032221_agenda">'
        "https://sfgov.org/youthcommission//event/2021/CE032221_agenda"
        "</a></div></div></div>  </div>"
    )


def test_links(parsed_event):
    assert parsed_event["links"] == [
        {"href": "https://sfbos.org/events/calendar", "title": "All Events"},
        {
            "href": (
                "https://sfbos.org/events/calendar/month/?field_event_category_tid=91"
            ),
            "title": "Youth Commission",
        },
        {
            "href": (
                "https://sfbos.org/event/"
                "youth-commission-civic-engagement-committee-cancelled-12"
            ),
            "title": "Youth Commission - Civic Engagement Committee (Cancelled)",
        },
    ]
