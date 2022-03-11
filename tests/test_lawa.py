from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.lawa import LawaSpider

test_response = file_response(
    join(dirname(__file__), "files", "lawa.html"),
    url="http://lawa.granicus.com/ViewPublisher.php?view_id=4",
)
spider = LawaSpider()

freezer = freeze_time("2022-03-07")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Regular Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 3, 3, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "lawa/202203031000/x/regular_meeting"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {"name": "", "address": ""}


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://lawa.granicus.com/ViewPublisher.php?view_id=4"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://lawa.granicus.com/AgendaViewer.php?view_id=4&clip_id=838",
            "title": "Agenda",
        },
        {
            "href": "http://lawa.granicus.com/MediaPlayer.php?view_id=4&clip_id=838",
            "title": "Video",
        },
        {
            "href": "http://lawa.granicus.com/ASX.php?view_id=4&clip_id=838&sn="
            "lawa.granicus.com",
            "title": "Open Video Only in Windows Media Player",
        },
        {
            "href": "http://archive-media.granicus.com:443/OnDemand/lawa/"
            "lawa_84b256f4-2683-46e5-8aa0-7b678a6b79c7.mp4",
            "title": "MP4 Video",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
