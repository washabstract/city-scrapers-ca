from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.west_hollywood import WestHollywoodSpider

test_response_city_council = file_response(
    join(dirname(__file__), "files", "west_hollywood_city_council.html"),
    url="https://weho.granicus.com/ViewPublisher.php?view_id=22",
)
test_response_planning_commission = file_response(
    join(dirname(__file__), "files", "west_hollywood_planning_commission.html"),
    url="https://weho.granicus.com/ViewPublisher.php?view_id=31",
)
spider = WestHollywoodSpider()

freezer = freeze_time("2022-03-01")
freezer.start()

city_council_items = [item for item in spider.parse(test_response_city_council)]
planning_commission_items = [
    item for item in spider.parse(test_response_planning_commission)
]

parsed_items = city_council_items + planning_commission_items

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Regular City Council Meeting"
    assert parsed_items[400]["title"] == "Planning Commission Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[400]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 2, 22, 18, 0)
    assert parsed_items[400]["start"] == datetime(2018, 3, 1, 18, 30)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[400]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[400]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "west_hollywood/202202221800/x/regular_city_council_meeting"
    )
    assert (
        parsed_items[400]["id"]
        == "west_hollywood/201803011830/x/planning_commission_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[400]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {}
    assert parsed_items[400]["location"] == {}


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://weho.granicus.com/ViewPublisher.php?view_id=22"
    )
    assert (
        parsed_items[400]["source"]
        == "https://weho.granicus.com/ViewPublisher.php?view_id=31"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://weho.granicus.com/MediaPlayer.php?view_id=22&clip_id=3733",
            "title": "Video",
        },
        {
            "href": "http://weho.granicus.com/AgendaViewer.php?view_id=22&clip_id=3733",
            "title": "Agenda",
        },
        {
            "href": "http://archive-media.granicus.com:443/OnDemand/weho/"
            "weho_ec7f02b9-6c22-4e15-992f-7de6312824db.mp3",
            "title": "MP3 Audio",
        },
        {
            "href": "http://archive-media.granicus.com:443/OnDemand/weho/"
            "weho_ec7f02b9-6c22-4e15-992f-7de6312824db.mp4",
            "title": "MP4 Video",
        },
    ]
    assert parsed_items[400]["links"] == [
        {
            "href": "http://weho.granicus.com/MediaPlayer.php?view_id=31&clip_id=3190",
            "title": "Video",
        },
        {
            "href": "http://weho.granicus.com/AgendaViewer.php?view_id=31&clip_id=3190",
            "title": "Agenda",
        },
        {
            "href": "http://archive-media.granicus.com:443/OnDemand/weho/"
            "weho_2c7ea8ca-c1bc-4f24-b3a9-d141eb303efa.mp3",
            "title": "MP3 Audio",
        },
        {
            "href": "http://archive-media.granicus.com:443/OnDemand/weho/"
            "weho_2c7ea8ca-c1bc-4f24-b3a9-d141eb303efa.mp4",
            "title": "MP4 Video",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[400]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
