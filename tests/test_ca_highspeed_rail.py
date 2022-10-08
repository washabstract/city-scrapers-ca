from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.ca_highspeed_rail import CaHighspeedRailSpider

test_response = file_response(
    join(dirname(__file__), "files", "ca_highspeed_rail.html"),
    url="https://hsr.ca.gov/about/board-of-directors/schedule/",
)
test_finance_committee_response = file_response(
    join(dirname(__file__), "files", "ca_highspeed_rail_finance_committee.html"),
    url="https://hsr.ca.gov/about/board-of-directors/finance-audit-committee/",
)
test_special_matters_committee_response = file_response(
    join(dirname(__file__), "files", "ca_highspeed_rail_special_committee.html"),
    url="https://hsr.ca.gov/about/board-of-directors/special-matters-committee/",
)

spider = CaHighspeedRailSpider()

freezer = freeze_time("2022-10-04")
freezer.start()

# parsed_items[0] is upcoming
# parsed_items[3] is a past item
parsed_items = [item for item in spider.parse(test_response)]
parsed_items_finance_committee = [
    item for item in spider.parse(test_finance_committee_response)
]
parsed_items_special_matters_committee = [
    item for item in spider.parse(test_special_matters_committee_response)
]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board Meeting"
    assert parsed_items_finance_committee[0]["title"] == "Finance & Audit Committee"
    assert (
        parsed_items_special_matters_committee[0]["title"]
        == "Special Matters Committee"
    )


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[3]["description"] == ""
    assert parsed_items_finance_committee[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 10, 20, 10, 0)
    assert parsed_items[3]["start"] == datetime(2022, 9, 15, 10, 0)
    assert parsed_items_finance_committee[0]["start"] == datetime(2022, 9, 15, 10, 0)
    assert parsed_items_special_matters_committee[0]["start"] == datetime(
        2021, 3, 29, 10, 0
    )


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[3]["end"] is None
    assert parsed_items_finance_committee[0]["end"] is None
    assert parsed_items_special_matters_committee[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[3]["time_notes"] == ""
    assert parsed_items_finance_committee[0]["time_notes"] == ""
    assert parsed_items_special_matters_committee[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "ca_highspeed_rail/202210201000/x/board_meeting"
    assert (
        parsed_items_finance_committee[0]["id"]
        == "ca_highspeed_rail/202209151000/x/finance_audit_committee"
    )
    assert (
        parsed_items_special_matters_committee[0]["id"]
        == "ca_highspeed_rail/202103291000/x/special_matters_committee"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[3]["status"] == PASSED
    assert parsed_items_finance_committee[0]["status"] == PASSED
    assert parsed_items_special_matters_committee[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "California High-Speed Rail Authority",
        "address": "770 L Street, Suite 620 Sacramento, CA 95814",
    }

    assert parsed_items_finance_committee[0]["location"] == {
        "name": "California High-Speed Rail Authority",
        "address": "770 L Street, Suite 620 Sacramento, CA 95814",
    }

    assert parsed_items_special_matters_committee[0]["location"] == {
        "name": "California High-Speed Rail Authority",
        "address": "770 L Street, Suite 620 Sacramento, CA 95814",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://hsr.ca.gov/about/board-of-directors/schedule/"
    )
    assert (
        parsed_items[3]["source"]
        == "https://hsr.ca.gov/about/board-of-directors/schedule/"
    )
    assert (
        parsed_items_finance_committee[0]["source"]
        == "https://hsr.ca.gov/about/board-of-directors/finance-audit-committee/"
    )
    assert (
        parsed_items_special_matters_committee[0]["source"]
        == "https://hsr.ca.gov/about/board-of-directors/special-matters-committee/"
    )


def test_links():
    # Asserting the first two items
    assert parsed_items[0]["links"] == []
    assert parsed_items[3]["links"][:2] == [
        {
            "href": "https://hsr.ca.gov/2022/09/05/board-of-directors-meeting-4/",
            "title": "September 15, 2022 Board Meeting Agenda",
        },
        {
            "href": "https://youtu.be/ShlVl2Tf6y0",
            "title": "September 15, 2022 Board Meeting Video",
        },
    ]

    assert parsed_items_finance_committee[0]["links"][:2] == [
        {
            "title": "September 15, 2022 Finance & Audit Committee Agenda",
            "href": "https://hsr.ca.gov/2022/08/15/finance-and-audit-committee-agenda/",
        },
        {
            "title": "September 15, 2022 Finance & Audit Committee Video",
            "href": "https://youtu.be/OYerQMqeJYM",
        },
    ]

    assert parsed_items_special_matters_committee[0]["links"] == []
    assert parsed_items_special_matters_committee[1]["links"] == [
        {
            "href": "https://hsr.ca.gov/wp-content/uploads"
            "/2021/04/brdmtg_032221_SM_Committee_Agenda.pdf",
            "title": "March 22, 2021 Special Matters Committee Meeting Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items_finance_committee[0]["classification"] == COMMITTEE
    assert parsed_items_special_matters_committee[0]["classification"] == COMMITTEE


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
