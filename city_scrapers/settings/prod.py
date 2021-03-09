import os

from .base import *  # noqa

USER_AGENT = "City Scrapers [production mode]. Learn more and say hello at https://citybureau.org/city-scrapers"  # noqa

# Configure item pipelines
ITEM_PIPELINES = {
    "scrapy.pipelines.files.FilesPipeline": 100,
    "city_scrapers_core.pipelines.GCSDiffPipeline": 200,
    "city_scrapers_core.pipelines.MeetingPipeline": 300,
    "city_scrapers_core.pipelines.OpenCivicDataPipeline": 400,
}

SENTRY_DSN = os.getenv("SENTRY_DSN")

EXTENSIONS = {
    "scrapy_sentry.extensions.Errors": 10,
    "city_scrapers_core.extensions.GCSStatusExtension": 100,
    "scrapy.extensions.closespider.CloseSpider": None,
}

FEED_EXPORTERS = {
    "json": "scrapy.exporters.JsonItemExporter",
    "jsonlines": "scrapy.exporters.JsonLinesItemExporter",
}

FEED_FORMAT = "jsonlines"

FEED_STORAGES = {
    "gcs": "scrapy.extensions.feedexport.GCSFeedStorage",
}

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCS_BUCKET = os.getenv("GCS_BUCKET")
CITY_SCRAPERS_STATUS_BUCKET = GCS_BUCKET

FEED_URI = (
    "gs://{bucket}/%(year)s/%(month)s/%(day)s/%(hour_min)s/%(name)s.json"
).format(bucket=GCS_BUCKET)
