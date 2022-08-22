from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.walnut_creek import WalnutCreekSpider

test_response = file_response(
    join(dirname(__file__), "files", "walnut_creek.html"),
    url="https://walnutcreek.granicus.com/ViewPublisher.php?view_id=12",
)
spider = WalnutCreekSpider()

freezer = freeze_time("2022-07-26")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
test_response_110 = file_response(
    join("tests", "files", "walnut_creek_110.html"), url=parsed_items[110].url
)
test_response_110.headers["Content-Type"] = "text/html"
parsed_items[110] = next(
    spider._parse_time_location(
        test_response_110,
        parsed_items[110]._cb_kwargs["meeting"],
        parsed_items[110]._cb_kwargs["item"],
    )
)

test_response_1170 = file_response(
    join("tests", "files", "walnut_creek_1170.html"), url=parsed_items[1170].url
)
test_response_1170.headers["Content-Type"] = "text/html"
parsed_items[1170] = next(
    spider._parse_time_location(
        test_response_1170,
        parsed_items[1170]._cb_kwargs["meeting"],
        parsed_items[1170]._cb_kwargs["item"],
    )
)

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Planning Commission Meeting"
    assert (
        parsed_items[110]["title"]
        == "City Council Special Meeting, Closed Session - 4:00 PM & City Council "
        "Regular Meeting - 6:00 PM"
    )
    assert parsed_items[1170]["title"] == "Planning Commission Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[110]["description"] == ""
    assert parsed_items[1170]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 7, 28, 19, 0)
    assert parsed_items[110]["start"] == datetime(2022, 5, 17, 16, 0)
    assert parsed_items[1170]["start"] == datetime(2022, 5, 12, 19, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[0]["end"] is None
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[110]["time_notes"] == ""
    assert (
        parsed_items[1170]["time_notes"]
        == "There is also a virtual option for this meeting. Zoom Meeting ID: "
        "824 6704 7996 / Login Password: 749 941"
    )


def test_id():
    assert (
        parsed_items[0]["id"]
        == "walnut_creek/202207281900/x/planning_commission_meeting"
    )
    assert (
        parsed_items[110]["id"]
        == "walnut_creek/202205171600/x/city_council_special_meeting_closed_session_"
        "4_00_pm_city_council_regular_meeting_6_00_pm"
    )
    assert (
        parsed_items[1170]["id"]
        == "walnut_creek/202205121900/x/planning_commission_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[110]["status"] == PASSED
    assert parsed_items[1170]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {"name": "", "address": ""}
    assert parsed_items[110]["location"] == {
        "name": "Council Chamber, City Hall",
        "address": "Council Chamber, 1666 N Main St, Walnut Creek",
    }
    assert parsed_items[1170]["location"] == {
        "name": "Council Chamber, City Hall",
        "address": "Council Chamber, 1666 N Main St, Walnut Creek",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://walnutcreek.granicus.com/ViewPublisher.php?view_id=12"
    )
    assert (
        parsed_items[110]["source"]
        == "https://walnutcreek.granicus.com/ViewPublisher.php?view_id=12"
    )
    assert (
        parsed_items[1170]["source"]
        == "https://walnutcreek.granicus.com/ViewPublisher.php?view_id=12"
    )


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[110]["links"] == [
        {
            "href": "https://walnutcreek.granicus.com/MinutesViewer.php?view_id=12&"
            "clip_id=4496",
            "title": "Minutes",
        },
        {
            "href": "https://walnutcreek.granicus.com/MediaPlayer.php?view_id=12&"
            "clip_id=4496",
            "title": "Video",
        },
    ]
    assert parsed_items[1170]["links"] == [
        {
            "href": "https://walnutcreek.granicus.com/AgendaViewer.php?view_id=12&"
            "clip_id=4494",
            "title": "Agenda",
        },
        {
            "href": "https://walnutcreek.granicus.com/MediaPlayer.php?view_id=12&"
            "clip_id=4494",
            "title": "Video",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
    assert parsed_items[110]["classification"] == CITY_COUNCIL
    assert parsed_items[1170]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    if type(item) is Meeting:
        assert item["all_day"] is False
