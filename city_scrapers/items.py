import scrapy
from city_scrapers_core.items import Meeting as CoreMeeting


class Meeting(CoreMeeting):
    jsonschema = CoreMeeting.jsonschema
    created = scrapy.Field()
    jsonschema["properties"]["created"] = {
        "type": "string",
        "description": "The datetime the meeting object was created in local time in ISO 8601 format",  # noqa
        "format": "date-time",
    }
    updated = scrapy.Field()
    jsonschema["properties"]["updated"] = {
        "type": "string",
        "description": "The datetime the meeting object was last updated in local time in ISO 8601 format",  # noqa
        "format": "date-time",
    }
