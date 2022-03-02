from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.west_hollywood import WestHollywoodSpider

test_response = file_response(
    join(dirname(__file__), "files", "west_hollywood.html"),
    url="https://weho.granicus.com/ViewPublisher.php?view_id=22",
)
spider = WestHollywoodSpider()

freezer = freeze_time("2022-03-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Regular City Council Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 2, 22, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "west_hollywood/202202220000/x/regular_city_council_meeting"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {}


def test_source():
    assert(parsed_items[0]["source"] == 
    "https://weho.granicus.com/ViewPublisher.php?view_id=22")


def test_links():
    assert parsed_items[0]["links"] == [{
      "href": "http://weho.granicus.com/MediaPlayer.php?view_id=22&clip_id=3733",
      "title": "Video"
    },
    {
      "href": "http://weho.granicus.com/AgendaViewer.php?view_id=22&clip_id=3733",
      "title": "Agenda"
    },
    {
      "href": "http://archive-media.granicus.com:443/OnDemand/weho/"
      "weho_ec7f02b9-6c22-4e15-992f-7de6312824db.mp3",
      "title": "MP3 Audio"
    },
    {
      "href": "http://archive-media.granicus.com:443/OnDemand/weho/"
      "weho_ec7f02b9-6c22-4e15-992f-7de6312824db.mp4",
      "title": "MP4 Video"
    },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
