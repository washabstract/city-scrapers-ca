import os

from .base import *  # noqa

USER_AGENT = "City Scrapers [production mode]. Learn more and say hello at https://citybureau.org/city-scrapers"  # noqa

# Configure item pipelines
ITEM_PIPELINES = {
    "scrapy.pipelines.files.FilesPipeline": 100,
    "city_scrapers_core.pipelines.GCSDiffPipeline": 200,
    "city_scrapers_core.pipelines.MeetingPipeline": 300,
    "city_scrapers_core.pipelines.OpenCivicDataPipeline": 400,
    # "city_scrapers.pipelines.TextExtractorPipeline": 500,
    "city_scrapers.pipelines.PostgresPipeline": 600,
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

path = "{}/google-cloud-storage-credentials.json".format(os.getcwd())
credentials_content = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not os.path.exists(credentials_content):
    with open(path, "w") as f:
        f.write(credentials_content)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

FEED_URI = (
    "gs://{bucket}/%(year)s/%(month)s/%(day)s/%(hour_min)s/%(name)s.json"
).format(bucket=GCS_BUCKET)

POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
