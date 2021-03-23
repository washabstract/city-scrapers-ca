from datetime import date, datetime, timedelta
from os.path import dirname, join

from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.la_city_government import LaCityGovernmentSpider

test_response = file_response(
    join(dirname(__file__), "files", "la_city_government_calendar.html"),
    url=(
        "https://calendar.lacity.org/rest/views/calendar_rest_dynamic"
        "?display_id=services_1"
        "&display_id=services_1"
        "&filters%5Beventtype%5D=686"
        "&filters%5Bdepartment%5D="
        "&filters%5Btags%5D="
        "&filters%5Bstart%5D%5Bvalue%5D%5Bdate%5D="
        f"{str(date.today()-timedelta(days=14))}"
        "&filters%5Bend%5D%5Bvalue%5D%5Bdate%5D="
        f"{str(date.today()+timedelta(days=14))}"
    ),
)
spider = LaCityGovernmentSpider()

freezer = freeze_time("2021-02-26")
freezer.start()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Central Alameda NC Special Board Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 2, 26, 18, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "la_city_government/202102261830/x/"
        "central_alameda_nc_special_board_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "United States",
    }


def test_source():
    assert parsed_items[0]["source"] == (
        "https://calendar.lacity.org/rest/views/calendar_rest_dynamic"
        "?display_id=services_1"
        "&display_id=services_1"
        "&filters%5Beventtype%5D=686"
        "&filters%5Bdepartment%5D="
        "&filters%5Btags%5D="
        "&filters%5Bstart%5D%5Bvalue%5D%5Bdate%5D="
        f"{str(date.today()-timedelta(days=14))}"
        "&filters%5Bend%5D%5Bvalue%5D%5Bdate%5D="
        f"{str(date.today()+timedelta(days=14))}"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://ens.lacity.org/ensnc/centralalameda/"
            "ensnccentralalameda848148249_02262021.pdf",
            "title": "Meeting/Agenda Information",
        },
        {
            "href": "https://calendar.lacity.org/event/"
            "central-alameda-nc-special-board-meeting-14",
            "title": "Calendar Link",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_all_day():
    assert parsed_items[0]["all_day"] is False
