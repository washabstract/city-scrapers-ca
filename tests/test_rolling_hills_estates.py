from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CANCELLED, CITY_COUNCIL
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.rolling_hills_estates import RollingHillsEstatesSpider

start_url = "https://rollinghillsestatesca.granicus.com/ViewPublisher.php?view_id=1"
test_response = file_response(
    join(dirname(__file__), "files", "rolling_hills_estates.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "rolling_hills_estates_agenda_1.pdf"),
    url=start_url,
    mode="rb",
)

agenda_response2 = file_response(
    join(dirname(__file__), "files", "rolling_hills_estates_agenda_2.pdf"),
    url=start_url,
    mode="rb",
)

spider = RollingHillsEstatesSpider()

freezer = freeze_time("2022-12-19")
freezer.start()

agenda_start_time = spider._parse_pdf_start_time(agenda_response)
agenda2_start_time = spider._parse_pdf_start_time(agenda_response2)

parsed_items = [item for item in spider.parse(test_response)]
parsed_item1 = next(
    spider._parse_agenda(
        agenda_response2,
        parsed_items[1].cb_kwargs["meeting"],
        parsed_items[1].cb_kwargs["item"],
    )
)
parsed_items = [
    item.cb_kwargs["meeting"] if type(item) != Meeting else item
    for item in spider.parse(test_response)
]


freezer.stop()


def test_number_parsed():
    assert len(parsed_items) > 300


def test_title():
    assert parsed_items[0]["title"] == "City Council Meeting - CANCELED"
    assert parsed_items[2]["title"] == "City Council Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 27, 19, 0)
    assert agenda_start_time == datetime(2022, 12, 19, 19, 0)
    assert agenda2_start_time == datetime(2022, 12, 19, 19, 0)
    assert parsed_item1["start"] == datetime(2022, 12, 13, 19, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_item1["end"] == datetime(2022, 12, 13, 21, 11)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "rolling_hills_estates/202212271900/x/"
        "city_council_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == CANCELLED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "4045 PALOS VERDES DRIVE NORTH, ROLLING HILLS ESTATES, CA 90274",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://rollinghillsestatesca.granicus.com"
            "/AgendaViewer.php?view_id=1&event_id=669",
            "title": "Agenda",
        }
    ]

    assert parsed_items[1]["links"] == [
        {
            "href": "https://rollinghillsestatesca.granicus.com"
            "/AgendaViewer.php?view_id=1&clip_id=674",
            "title": "Agenda",
        },
        {
            "href": "https://rollinghillsestatesca.granicus.com"
            "/MediaPlayer.php?view_id=1&clip_id=674",
            "title": "Video",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
