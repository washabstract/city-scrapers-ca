from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.la_habra_heights import LaHabraHeightsSpider

start_url = "https://la-habra-heights.granicus.com/ViewPublisher.php?view_id=4"
test_response = file_response(
    join(dirname(__file__), "files", "la_habra_heights.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "la_habra_heights_agenda_1.pdf"),
    url=start_url,
    mode="rb",
)

spider = LaHabraHeightsSpider()

freezer = freeze_time("2022-12-21")
freezer.start()

agenda_start_time = spider._parse_pdf_start_time(agenda_response)
parsed_items = [
    item.cb_kwargs["meeting"] if type(item) != Meeting else item
    for item in spider.parse(test_response)
]

freezer.stop()


def test_number_parsed():
    assert len(parsed_items) > 300


def test_title():
    assert parsed_items[0]["title"] == "Regular Planning Commission Meeting"
    assert parsed_items[1]["title"] == "Regular Roads Advisory Committee Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 27, 18, 30)
    assert agenda_start_time == datetime(2022, 12, 21, 17, 30)
    assert parsed_items[4]["start"] == datetime(2022, 12, 12, 18, 48)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[4]["end"] == datetime(2022, 12, 12, 20, 9)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "la_habra_heights/202212271830/x/"
        "regular_planning_commission_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "1225 North Hacienda Road, La Habra Heights, California 90631",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == []

    assert parsed_items[4]["links"] == [
        {
            "href": "https://la-habra-heights.granicus.com"
            "/AgendaViewer.php?view_id=4&clip_id=886",
            "title": "Agenda",
        },
        {
            "href": "https://la-habra-heights.granicus.com"
            "/MediaPlayer.php?view_id=4&clip_id=886",
            "title": "Video",
        },
        {
            "href": "https://archive-video.granicus.com"
            "/la-habra-height/la-habra-height_84cdee15-c652-4d83-b6cf-7498ccdf1c82.mp3",
            "title": "MP3 Audio",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
