from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import ADVISORY_COMMITTEE, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.ccta import CctaSpider

test_response = file_response(
    join(dirname(__file__), "files", "ccta.html"),
    url="https://ccta.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings",
)
spider = CctaSpider()

freezer = freeze_time("2022-07-21")
freezer.start()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Countywide Bicycle and Pedestrian Advisory Committee Meeting"
    )


def test_description():
    assert parsed_items[0]["description"] == (
        "This meeting does not allow public speakers. "
        "This meeting does not allow public speakers."
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 7, 25, 11, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == (
        "ccta/202207251100/x/"
        "countywide_bicycle_and_pedestrian_advisory_committee_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {"name": "", "address": ""}


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://ccta.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://ccta.primegov.com/Portal/Meeting?"
            "compiledMeetingDocumentFileId=15222",
            "title": "HTML Packet",
        },
        {
            "href": "https://ccta.primegov.com/Public/CompiledDocument/15224",
            "title": "Agenda",
        },
        {
            "href": "https://ccta.primegov.com/Public/CompiledDocument/15223",
            "title": "Packet",
        },
        {"href": "https://youtube.com/watch?v=W2F0wRpVu68", "title": "Video Link"},
    ]


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


def test_all_day():
    assert parsed_items[0]["all_day"] is False
