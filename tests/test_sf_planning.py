from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.sf_planning import SfPlanningSpider

test_response = file_response(
    join(dirname(__file__), "files", "sf_planning.html"),
    url="https://sfplanning.org/event/planning-commission-151",
)
spider = SfPlanningSpider()

freezer = freeze_time("2021-10-27")
freezer.start()
parsed_items = [item for item in spider.parse_meeting(test_response)]
freezer.stop()




def test_title():
    assert parsed_items[0]["title"] == "Hearing for SF Planning Commission"


def test_description():
    assert len(parsed_items[0]["description"]) == 7212


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 10, 28, 13, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "sf_planning/202110281300/x/hearing_for_sf_planning_commission"


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "Stream at https://sfgovtv.org/planning – Public Comment: (415) 655-0001 / Access Code: 2486 151 4664",
        "name": "SF Planning Commission"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://sfplanning.org/event/planning-commission-151"


def test_links():
    assert parsed_items[0]["links"] == [{
      "href": "https://sfplanning.org/sites/default/files/agendas/2021-10/20211028_cal.pdf",
      "title": "Meeting/Agenda Information"
    },
    {
        "href": "https://sfplanning.org/resource/planning-commission-packet-october-28-2021",
        "title": "Supporting Documents"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
