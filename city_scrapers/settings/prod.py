import os

from .base import *  # noqa

USER_AGENT = "City Scrapers [production mode]. Learn more and say hello at https://citybureau.org/city-scrapers"  # noqa

# Configure item pipelines
ITEM_PIPELINES = {
    "scrapy.pipelines.files.FilesPipeline": 100,
    "city_scrapers.pipelines.S3DiffPipeline": 200,
    "city_scrapers_core.pipelines.MeetingPipeline": 300,
    "city_scrapers.pipelines.OpenCivicDataPipeline": 400,
    "city_scrapers.pipelines.TextExtractorPipeline": 500,
    "city_scrapers.pipelines.PostgresPipeline": 600,
}

SENTRY_DSN = os.getenv("SENTRY_DSN")

EXTENSIONS = {
    "scrapy_sentry.extensions.Errors": 10,
    "city_scrapers_core.extensions.S3StatusExtension": 100,
    "scrapy.extensions.closespider.CloseSpider": None,
}

FEED_EXPORTERS = {
    "json": "scrapy.exporters.JsonItemExporter",
    "jsonlines": "scrapy.exporters.JsonLinesItemExporter",
}

FEED_FORMAT = "jsonlines"

FEED_STORAGES = {
    "s3": "scrapy.extensions.feedexport.S3FeedStorage",
}

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
CITY_SCRAPERS_STATUS_BUCKET = S3_BUCKET

FEED_URI = (
    "s3://{bucket}/%(year)s/%(month)s/%(day)s/%(hour_min)s/%(name)s.json"
).format(bucket=S3_BUCKET)

POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
POSTGRES_USER_NEW = os.getenv("POSTGRES_USER_NEW")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

LOG_LEVEL = "WARNING"

# TODO: ScrapyDeprecationWarning: The `FEED_URI` and `FEED_FORMAT` settings have been
# deprecated in favor of the `FEEDS` setting. Please see the `FEEDS` setting docs for
# more details

# TODO: ScrapyDeprecationWarning: GCSFeedStorage.from_crawler does not support the
# 'feed_options' keyword argument. Add a 'feed_options' parameter to its signature to
# remove this warning. This parameter will become mandatory in a future version.
