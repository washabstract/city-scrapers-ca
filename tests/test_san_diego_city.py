from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import (
    CITY_COUNCIL,
    COMMISSION,
    COMMITTEE,
    PASSED,
    TENTATIVE,
)
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.san_diego_city import SanDiegoCitySpider

test_response = file_response(
    join(dirname(__file__), "files", "san_diego_city.html"),
    url="https://sandiego.granicus.com/ViewPublisher.php?view_id=3",
)

upcoming_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_upcoming.html"),
    url="https://sandiego.hylandcloud.com/211agendaonlinecouncil",
)

planning_commission_archived_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_planning_archived.html"),
    url="https://sandiego.granicus.com/ViewPublisher.php?view_id=8",
)

committee_upcoming_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_committee_upcoming.html"),
    url="https://sandiego.hylandcloud.com/211agendaonlinecomm"
    "/Meetings/Search?dropid=4&mtids=131%2C114%2C119%2C102%2C116"
    "%2C115%2C133%2C122%2C120%2C121%2C132%2C123%2C117%2C127%2C134%2C118",
)

# The file with the list of upcoming agendas
planning_upcoming_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_planning_upcoming.html"),
    url="https://www.sandiego.gov/planning-commission/documents/agenda",
)

spider = SanDiegoCitySpider()

freezer = freeze_time("2022-09-20")
freezer.start()

# 11th object also contains meeting link
parsed_items = [item for item in spider.parse(test_response)]
parsed_items_upcoming = [item for item in spider.parse(upcoming_response)]
parsed_items_planning_commission_archived = [
    item for item in spider.parse(planning_commission_archived_response)
]
parsed_items_committee_upcoming = [
    item for item in spider.parse(committee_upcoming_response)
]
parsed_items_planning_upcoming = [
    item for item in spider.parse(planning_upcoming_response)
]

# The pdf file with the first agenda
planning_upcoming_agenda_response_0 = file_response(
    join(dirname(__file__), "files", "san_diego_city_planning_upcoming_follow_0.pdf"),
    mode="rb",
    url=parsed_items_planning_upcoming[0].url,
)

# The pdf file with the second agenda
planning_upcoming_agenda_response_1 = file_response(
    join(dirname(__file__), "files", "san_diego_city_planning_upcoming_follow_1.pdf"),
    mode="rb",
    url=parsed_items_planning_upcoming[1].url,
)

# Modifying the first two items of
# the planning's upcoming meetings with the followed responses
parsed_items_planning_upcoming[0] = next(
    spider._parse_planning(
        planning_upcoming_agenda_response_0,
        parsed_items_planning_upcoming[0].cb_kwargs["source"],
    )
)

parsed_items_planning_upcoming[1] = next(
    spider._parse_planning(
        planning_upcoming_agenda_response_1,
        parsed_items_planning_upcoming[1].cb_kwargs["source"],
    )
)

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Special Agenda"
    assert parsed_items[11]["title"] == "Tuesday Agenda Revised Added S500-S508"
    assert parsed_items_upcoming[0]["title"] == "Adjourned Agenda"
    assert (
        parsed_items_planning_commission_archived[0]["title"] == "Planning Commission"
    )
    assert (
        parsed_items_committee_upcoming[0]["title"]
        == "Revised - Land Use and Housing Committee Meeting - Updated 09/21/22"
    )
    assert parsed_items_planning_upcoming[0]["title"] == "Planning Commission"
    assert parsed_items_planning_upcoming[1]["title"] == "Planning Commission"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[11]["description"] == ""
    assert parsed_items_upcoming[0]["description"] == ""
    assert parsed_items_planning_commission_archived[0]["description"] == ""
    assert parsed_items_committee_upcoming[0]["description"] == ""
    assert parsed_items_planning_upcoming[0]["description"] == ""
    assert parsed_items_planning_upcoming[1]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 19, 0, 0)
    assert parsed_items_upcoming[0]["start"] == datetime(2022, 9, 27, 10, 0)
    assert parsed_items_planning_commission_archived[0]["start"] == datetime(
        2022, 9, 15, 0, 0
    )
    assert parsed_items_committee_upcoming[0]["start"] == datetime(2022, 9, 22, 13, 0)
    assert parsed_items_planning_upcoming[0]["start"] == datetime(2022, 9, 29, 9, 0)
    assert parsed_items_planning_upcoming[1]["start"] == datetime(2022, 9, 22, 9, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 9, 19, 7, 41)
    assert parsed_items_upcoming[0]["end"] is None
    assert parsed_items_planning_commission_archived[0]["end"] == datetime(
        2022, 9, 15, 3, 39
    )
    assert parsed_items_committee_upcoming[0]["end"] is None
    assert parsed_items_planning_upcoming[0]["end"] is None
    assert parsed_items_planning_upcoming[1]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[11]["time_notes"] == ""
    assert parsed_items_upcoming[0]["time_notes"] == ""
    assert parsed_items_planning_commission_archived[0]["time_notes"] == ""
    assert parsed_items_committee_upcoming[0]["time_notes"] == ""
    assert parsed_items_planning_upcoming[0]["time_notes"] == ""
    assert parsed_items_planning_upcoming[1]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "san_diego_city/202209190000/x/special_agenda"
    assert (
        parsed_items_upcoming[0]["id"]
        == "san_diego_city/202209271000/x/adjourned_agenda"
    )
    assert (
        parsed_items_planning_commission_archived[0]["id"]
        == "san_diego_city/202209150000/x/planning_commission"
    )
    assert parsed_items_committee_upcoming[0]["id"] == (
        "san_diego_city/202209221300/x"
        "/revised_land_use_and_housing_committee_meeting_updated_09_21_22"
    )
    assert (
        parsed_items_planning_upcoming[0]["id"]
        == "san_diego_city/202209290900/x/planning_commission"
    )
    assert (
        parsed_items_planning_upcoming[1]["id"]
        == "san_diego_city/202209220900/x/planning_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[11]["status"] == PASSED
    assert parsed_items_upcoming[0]["status"] == TENTATIVE
    assert parsed_items_planning_commission_archived[0]["status"] == PASSED
    assert parsed_items_committee_upcoming[0]["status"] == TENTATIVE
    assert parsed_items_planning_upcoming[0]["status"] == TENTATIVE
    assert parsed_items_planning_upcoming[1]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }

    assert parsed_items[11]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }

    assert parsed_items_upcoming[0]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }

    assert parsed_items_planning_commission_archived[0]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }

    assert parsed_items_committee_upcoming[0]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }

    assert parsed_items_planning_upcoming[0]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }

    assert parsed_items_planning_upcoming[1]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://sandiego.granicus.com/ViewPublisher.php?view_id=3"
    )
    assert (
        parsed_items[11]["source"]
        == "https://sandiego.granicus.com/ViewPublisher.php?view_id=3"
    )
    assert (
        parsed_items_upcoming[0]["source"]
        == "https://sandiego.hylandcloud.com/211agendaonlinecouncil"
    )
    assert (
        parsed_items_planning_commission_archived[0]["source"]
        == "https://sandiego.granicus.com/ViewPublisher.php?view_id=8"
    )
    assert parsed_items_committee_upcoming[0]["source"] == (
        "https://sandiego.hylandcloud.com/211agendaonlinecomm"
        "/Meetings/Search?dropid=4&mtids=131%2C114%2C119%2C102%"
        "2C116%2C115%2C133%2C122%2C120%2C121%2C132%2C123%2C117%2C127%2C134%2C118"
    )
    assert (
        parsed_items_planning_upcoming[0]["source"]
        == "https://www.sandiego.gov/planning-commission/documents/agenda"
    )
    assert (
        parsed_items_planning_upcoming[1]["source"]
        == "https://www.sandiego.gov/planning-commission/documents/agenda"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=3&clip_id=8527",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/"
            "sandiego_f399b0df-ff5a-45b5-a6ac-b5c043699f0d.mp4",
        },
    ]

    assert parsed_items[11]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=3&clip_id=8477",
        },
        {
            "title": "Minutes",
            "href": "https://sandiego.granicus.com"
            "/MinutesViewer.php?view_id=3&clip_id=8477",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/"
            "sandiego_19ab90c2-2f55-41f5-98e9-dba3693f14de.mp4",
        },
    ]

    assert parsed_items_upcoming[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://sandiego.hylandcloud.com"
            "/211agendaonlinecouncil/Meetings/"
            "ViewMeeting?id=5262&doctype=1&site=council",
        }
    ]

    assert parsed_items_planning_commission_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=8&clip_id=8525",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/"
            "sandiego_184992d0-3969-47b3-a95e-0d8ba4fff916.mp4",
        },
    ]

    assert parsed_items_committee_upcoming[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://sandiego.hylandcloud.com/"
            "211agendaonlinecomm/Meetings/ViewMeeting?id=5257&doctype=1&site=comm",
        }
    ]

    assert parsed_items_committee_upcoming[1]["links"] == [
        {
            "title": "Agenda",
            "href": "https://sandiego.hylandcloud.com"
            "/211agendaonlinecomm/Meetings/ViewMeeting?id=5252&doctype=1&site=comm",
        },
        {
            "title": "Actions",
            "href": "https://sandiego.hylandcloud.com"
            "/211agendaonlinecomm/Meetings/ViewMeeting?id=5252&doctype=2&site=comm",
        },
    ]

    assert parsed_items_planning_upcoming[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://www.sandiego.gov/"
            "sites/default/files/dsd_pc_agenda_9-29-22.pdf",
        }
    ]

    assert parsed_items_planning_upcoming[1]["links"] == [
        {
            "title": "Agenda",
            "href": "https://www.sandiego.gov/"
            "sites/default/files/pc_agenda_9-22-22.pdf",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[11]["classification"] == CITY_COUNCIL
    assert parsed_items_upcoming[0]["classification"] == CITY_COUNCIL
    assert parsed_items_planning_commission_archived[0]["classification"] == COMMISSION
    assert parsed_items_committee_upcoming[0]["classification"] == COMMITTEE
    assert parsed_items_planning_upcoming[1]["classification"] == COMMISSION
    assert parsed_items_planning_upcoming[1]["classification"] == COMMISSION


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
