from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.la_city_government import LaCityGovernmentSpider

test_response = file_response(
    join(dirname(__file__), "files", "la_city_government.html"),
    url="https://lacity.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings",
)
spider = LaCityGovernmentSpider()

freezer = freeze_time("2021-10-21")
freezer.start()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Information, Technology, and General Services"


def test_description():
    assert parsed_items[0]["description"] == (
        "This meeting does not allow public speakers. "
        "This meeting does not allow public speakers."
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 10, 21, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == (
        "la_city_government/202110211000/x/"
        "information_technology_and_general_services"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "",
    }


def test_source():
    assert parsed_items[0]["source"] == (
        "https://lacity.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://lacity.primegov.com/Portal/Meeting?"
            "compiledMeetingDocumentFileId=13568",
            "title": "HTML Agenda",
        },
        {
            "href": "https://lacity.primegov.com/Public/CompiledDocument/13566",
            "title": "Agenda",
        },
        {
            "href": "https://lacity.primegov.com/Portal/Meeting?"
            "compiledMeetingDocumentFileId=13870",
            "title": "HTML Journal",
        },
        {
            "href": "https://lacity.primegov.com/Public/CompiledDocument/13867",
            "title": "Journal",
        },
        {
            "href": "https://youtube.com/watch?v=XsG8X1NTEoo",
            "title": "Video Link",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


def test_all_day():
    assert parsed_items[0]["all_day"] is False
