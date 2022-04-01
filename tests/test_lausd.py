from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.lausd import LausdSpider

test_response = file_response(
    join(dirname(__file__), "files", "lausd.html"),
    url="http://laschoolboard.org/LAUSDBdMtgAgendas",
)
spider = LausdSpider()

freezer = freeze_time("2022-02-24")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Curriculum and Instruction Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 2, 24, 16, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "lausd/202202241600/x/curriculum_and_instruction_committee"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {"address": "", "name": "",}


def test_source():
    assert parsed_items[0]["source"] == "http://laschoolboard.org/LAUSDBdMtgAgendas"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://www.laschoolboard.org/sites/default/files/"
            "02-24-22CIAAgendaPost.pdf",
            "title": "Agenda",
        },
        {
            "href": "http://lausd.granicus.com/MediaPlayer.php?publish_id=18",
            "title": "Live Video Link",
        },
        {"href": "http://laschoolboard.org/02-24-22CIA", "title": "Meeting Event Page"},
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
