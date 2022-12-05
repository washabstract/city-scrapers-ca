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

fire_ad_hoc_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_fire_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=28",
)

audit_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_audit_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=24",
)

budget_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_budget_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=16",
)

charter_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_chart_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=25",
)

government_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_gov_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=13",
)

land_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_land_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=12",
)

nrc_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_nrc_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=14",
)

public_safety_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_publicsafety_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=15",
)

rules_committee_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_rules_com_archived.html"),
    url="http://sandiego.granicus.com/ViewPublisher.php?view_id=11",
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
parsed_items_fire_archived = [
    item for item in spider.parse(fire_ad_hoc_committee_response)
]
parsed_items_audit_archived = [item for item in spider.parse(audit_committee_response)]
parsed_items_budget_archived = [
    item for item in spider.parse(budget_committee_response)
]
parsed_items_charter_archived = [
    item for item in spider.parse(charter_committee_response)
]
parsed_item_government_archived = [
    item for item in spider.parse(government_committee_response)
]
parsed_items_land_archived = [item for item in spider.parse(land_committee_response)]
parsed_items_nrc_archived = [item for item in spider.parse(nrc_committee_response)]
parsed_items_publicsafety_archived = [
    item for item in spider.parse(public_safety_committee_response)
]
parsed_items_rules_archived = [item for item in spider.parse(rules_committee_response)]

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
    assert (
        parsed_items_fire_archived[0]["title"]
        == "Ad Hoc Committee on Fire Prevention and Recovery"
    )
    assert parsed_items_audit_archived[0]["title"] == "Audit Committee Meeting"
    assert parsed_items_budget_archived[0]["title"] == "Budget and Finance Committee"
    assert parsed_items_charter_archived[0]["title"] == "Charter Review Committee"
    assert (
        parsed_item_government_archived[0]["title"]
        == "Government Efficiency & Openness (GE&O)"
    )
    assert parsed_items_land_archived[0]["title"] == "Land Use and Housing Committee"
    assert (
        parsed_items_nrc_archived[0]["title"] == "Natural Resources and Culture (NR&C)"
    )
    assert (
        parsed_items_publicsafety_archived[0]["title"]
        == "Public Safety and Neighborhood Services (PS&NS)"
    )
    assert parsed_items_rules_archived[0]["title"] == "Rules Committee"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[11]["description"] == ""
    assert parsed_items_upcoming[0]["description"] == ""
    assert parsed_items_planning_commission_archived[0]["description"] == ""
    assert parsed_items_committee_upcoming[0]["description"] == ""
    assert parsed_items_planning_upcoming[0]["description"] == ""
    assert parsed_items_planning_upcoming[1]["description"] == ""
    assert parsed_items_fire_archived[0]["description"] == ""
    assert parsed_items_audit_archived[0]["description"] == ""
    assert parsed_items_budget_archived[0]["description"] == ""
    assert parsed_items_charter_archived[0]["description"] == ""
    assert parsed_item_government_archived[0]["description"] == ""
    assert parsed_items_land_archived[0]["description"] == ""
    assert parsed_items_nrc_archived[0]["description"] == ""
    assert parsed_items_publicsafety_archived[0]["description"] == ""
    assert parsed_items_rules_archived[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 19, 0, 0)
    assert parsed_items_upcoming[0]["start"] == datetime(2022, 9, 27, 10, 0)
    assert parsed_items_planning_commission_archived[0]["start"] == datetime(
        2022, 9, 15, 0, 0
    )
    assert parsed_items_committee_upcoming[0]["start"] == datetime(2022, 9, 22, 13, 0)
    assert parsed_items_planning_upcoming[0]["start"] == datetime(2022, 9, 29, 9, 0)
    assert parsed_items_planning_upcoming[1]["start"] == datetime(2022, 9, 22, 9, 0)
    assert parsed_items_fire_archived[0]["start"] == datetime(2008, 11, 10, 0, 0)
    assert parsed_items_audit_archived[0]["start"] == datetime(2022, 9, 21, 0, 0)
    assert parsed_items_budget_archived[0]["start"] == datetime(2013, 11, 21, 0, 0)
    assert parsed_items_charter_archived[0]["start"] == datetime(2016, 5, 18, 0, 0)
    assert parsed_item_government_archived[0]["start"] == datetime(2005, 12, 5, 0, 0)
    assert parsed_items_land_archived[0]["start"] == datetime(2022, 9, 22, 0, 0)
    assert parsed_items_nrc_archived[0]["start"] == datetime(2013, 11, 6, 0, 0)
    assert parsed_items_publicsafety_archived[0]["start"] == datetime(
        2013, 10, 30, 0, 0
    )
    assert parsed_items_rules_archived[0]["start"] == datetime(2022, 9, 21, 0, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 9, 19, 7, 41)
    assert parsed_items_upcoming[0]["end"] is None
    assert parsed_items_planning_commission_archived[0]["end"] == datetime(
        2022, 9, 15, 3, 39
    )
    assert parsed_items_committee_upcoming[0]["end"] is None
    assert parsed_items_planning_upcoming[0]["end"] is None
    assert parsed_items_planning_upcoming[1]["end"] is None
    assert parsed_items_fire_archived[0]["end"] == datetime(2008, 11, 10, 0, 56)
    assert parsed_items_audit_archived[0]["end"] == datetime(2022, 9, 21, 2, 18)
    assert parsed_items_budget_archived[0]["end"] == datetime(2013, 11, 21, 0, 0)
    assert parsed_items_charter_archived[0]["end"] == datetime(2016, 5, 18, 3, 18)
    assert parsed_item_government_archived[0]["end"] == datetime(2005, 12, 5, 0, 44)
    assert parsed_items_land_archived[0]["end"] == datetime(2022, 9, 22, 0, 44)
    assert parsed_items_nrc_archived[0]["end"] == datetime(2013, 11, 6, 2, 58)
    assert parsed_items_publicsafety_archived[0]["end"] == datetime(2013, 10, 30, 4, 2)
    assert parsed_items_rules_archived[0]["end"] == datetime(2022, 9, 21, 1, 26)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[11]["time_notes"] == ""
    assert parsed_items_upcoming[0]["time_notes"] == ""
    assert parsed_items_planning_commission_archived[0]["time_notes"] == ""
    assert parsed_items_committee_upcoming[0]["time_notes"] == ""
    assert parsed_items_planning_upcoming[0]["time_notes"] == ""
    assert parsed_items_planning_upcoming[1]["time_notes"] == ""
    assert parsed_items_fire_archived[0]["time_notes"] == ""
    assert parsed_items_audit_archived[0]["time_notes"] == ""
    assert parsed_items_budget_archived[0]["time_notes"] == ""
    assert parsed_items_charter_archived[0]["time_notes"] == ""
    assert parsed_item_government_archived[0]["time_notes"] == ""
    assert parsed_items_land_archived[0]["time_notes"] == ""
    assert parsed_items_nrc_archived[0]["time_notes"] == ""
    assert parsed_items_publicsafety_archived[0]["time_notes"] == ""
    assert parsed_items_rules_archived[0]["time_notes"] == ""


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
    assert (
        parsed_items_fire_archived[0]["id"] == "san_diego_city/200811100000/x/"
        "ad_hoc_committee_on_fire_prevention_and_recovery"
    )
    assert (
        parsed_items_audit_archived[0]["id"]
        == "san_diego_city/202209210000/x/audit_committee_meeting"
    )
    assert (
        parsed_items_budget_archived[0]["id"]
        == "san_diego_city/201311210000/x/budget_and_finance_committee"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[11]["status"] == PASSED
    assert parsed_items_upcoming[0]["status"] == TENTATIVE
    assert parsed_items_planning_commission_archived[0]["status"] == PASSED
    assert parsed_items_committee_upcoming[0]["status"] == TENTATIVE
    assert parsed_items_planning_upcoming[0]["status"] == TENTATIVE
    assert parsed_items_planning_upcoming[1]["status"] == TENTATIVE
    assert parsed_items_fire_archived[0]["status"] == PASSED
    # Scraped after the freeze date
    assert parsed_items_audit_archived[0]["status"] == TENTATIVE
    assert parsed_items_budget_archived[0]["status"] == PASSED
    assert parsed_items_charter_archived[0]["status"] == PASSED
    assert parsed_item_government_archived[0]["status"] == PASSED
    assert parsed_items_land_archived[0]["status"] == TENTATIVE
    assert parsed_items_nrc_archived[0]["status"] == PASSED
    assert parsed_items_publicsafety_archived[0]["status"] == PASSED
    assert parsed_items_rules_archived[0]["status"] == TENTATIVE


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

    assert (
        parsed_items_fire_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=28"
    )
    assert (
        parsed_items_audit_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=24"
    )
    assert (
        parsed_items_budget_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=16"
    )
    assert (
        parsed_items_charter_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=25"
    )
    assert (
        parsed_item_government_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=13"
    )
    assert (
        parsed_items_land_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=12"
    )
    assert (
        parsed_items_nrc_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=14"
    )
    assert (
        parsed_items_publicsafety_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=15"
    )
    assert (
        parsed_items_rules_archived[0]["source"]
        == "http://sandiego.granicus.com/ViewPublisher.php?view_id=11"
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

    assert parsed_items_fire_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com/"
            "MediaPlayer.php?view_id=28&clip_id=2574",
        },
        {
            "title": "Audio",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_4d73ae5c-9e4a-467b-a313-57d2c7d95bde.mp3",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_4d73ae5c-9e4a-467b-a313-57d2c7d95bde.mp4",
        },
    ]
    assert parsed_items_audit_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=24&clip_id=8529",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_d051643c-23a6-45a1-b192-d78e8971c4a7.mp4",
        },
    ]
    assert parsed_items_budget_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=16&clip_id=5963",
        },
        {
            "title": "Audio",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_423dd213-5d1f-4a17-a47b-11fe9e767585.mp3",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_423dd213-5d1f-4a17-a47b-11fe9e767585.mp4",
        },
    ]
    assert parsed_items_charter_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=25&clip_id=6707",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_bbe37559-0765-4535-90b2-86bbf42d18b0.mp4",
        },
    ]
    assert parsed_item_government_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=13&clip_id=412",
        },
        {
            "title": "Audio",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_021929f55b7fd4e36b3275ad8f912ee5.mp3",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_021929f55b7fd4e36b3275ad8f912ee5.mp4",
        },
    ]
    assert parsed_items_land_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=12&clip_id=8534",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_ffe8723b-19eb-4ea4-aded-0152d6ccc062.mp4",
        },
    ]
    assert parsed_items_nrc_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=14&clip_id=5951",
        },
        {
            "title": "Audio",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_6395881e-b8f6-4067-9146-69b21283b018.mp3",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_6395881e-b8f6-4067-9146-69b21283b018.mp4",
        },
    ]
    assert parsed_items_publicsafety_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=15&clip_id=5945",
        },
        {
            "title": "Audio",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_24fd2ac5-205d-4060-96db-5e02be2cf5c0.mp3",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_24fd2ac5-205d-4060-96db-5e02be2cf5c0.mp4",
        },
    ]
    assert parsed_items_rules_archived[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=11&clip_id=8530",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/sandiego_8f15d3b9-7716-47bb-aa05-b1f69ee7492a.mp4",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[11]["classification"] == CITY_COUNCIL
    assert parsed_items_upcoming[0]["classification"] == CITY_COUNCIL
    assert parsed_items_planning_commission_archived[0]["classification"] == COMMISSION
    assert parsed_items_committee_upcoming[0]["classification"] == COMMITTEE
    assert parsed_items_planning_upcoming[1]["classification"] == COMMISSION
    assert parsed_items_planning_upcoming[1]["classification"] == COMMISSION
    assert parsed_items_fire_archived[0]["classification"] == COMMITTEE
    assert parsed_items_audit_archived[0]["classification"] == COMMITTEE
    assert parsed_items_budget_archived[0]["classification"] == COMMITTEE
    assert parsed_items_charter_archived[0]["classification"] == COMMITTEE
    assert parsed_item_government_archived[0]["classification"] == COMMITTEE
    assert parsed_items_land_archived[0]["classification"] == COMMITTEE
    assert parsed_items_nrc_archived[0]["classification"] == COMMITTEE
    assert parsed_items_publicsafety_archived[0]["classification"] == COMMITTEE
    assert parsed_items_rules_archived[0]["classification"] == COMMITTEE


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
