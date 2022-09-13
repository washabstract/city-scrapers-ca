from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.metrolink import MetrolinkSpider

test_response = file_response(
    join(dirname(__file__), "files", "metrolink.html"),
    url="https://metrolink.granicus.com/ViewPublisher.php?view_id=8",
)
spider = MetrolinkSpider()

freezer = freeze_time("2022-09-09")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Audit and Finance Committee"
    assert parsed_items[6]["title"] == "Board of Directors"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[6]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 9, 9, 0)
    assert parsed_items[6]["start"] == datetime(2022, 7, 22, 9, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[6]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[6]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "metrolink/202209090900/x/audit_and_finance_committee"
    )
    assert parsed_items[6]["id"] == "metrolink/202207220900/x/board_of_directors"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[6]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "900 Wilshire Blvd, Riverside Conference Room, 12th Floor, "
        "Los Angeles, CA 90017",
        "name": "Metrolink Headquarters Building",
    }
    assert parsed_items[6]["location"] == {
        "address": "900 Wilshire Blvd, Riverside Conference Room, 12th Floor, "
        "Los Angeles, CA 90017",
        "name": "Metrolink Headquarters Building",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://metrolink.granicus.com/ViewPublisher.php?view_id=8"
    )
    assert (
        parsed_items[6]["source"]
        == "https://metrolink.granicus.com/ViewPublisher.php?view_id=8"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://metrolink.granicus.com/AgendaViewer.php?view_id=8"
            "&event_id=494",
            "title": "Agenda",
        }
    ]
    assert parsed_items[6]["links"] == [
        {
            "href": "https://metrolink.granicus.com/AgendaViewer.php?view_id=8"
            "&clip_id=913",
            "title": "Agenda",
        },
        {
            "href": "https://metrolink.granicus.com/MediaPlayer.php?view_id=8"
            "&clip_id=913",
            "title": "Video",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[6]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
