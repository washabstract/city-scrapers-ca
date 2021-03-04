import json
from datetime import datetime, timedelta
from operator import attrgetter
from typing import List, Mapping

from city_scrapers_core.pipelines import DiffPipeline
from pytz import timezone
from scrapy.crawler import Crawler


class GCSDiffPipeline(DiffPipeline):
    """Implements :class:`DiffPipeline` for Google Cloud Storage"""

    def __init__(self, crawler: Crawler, output_format: str):
        """Initialize :class:`GCSDiffPipeline` from crawler

        :param crawler: Current Crawler object
        :param output_format: Only "ocd" is supported
        """
        from google.cloud import storage

        self.spider = crawler.spider
        self.feed_prefix = crawler.settings.get(
            "CITY_SCRAPERS_DIFF_FEED_PREFIX", "%Y/%m/%d"
        )
        self.bucket_name = crawler.settings.get("GCS_BUCKET")
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
        super().__init__(crawler, output_format)

    def load_previous_results(self) -> List[Mapping]:
        """Load previously scraped items on Google Cloud Storage

        :return: Previously scraped results
        """
        max_days_previous = 3
        days_previous = 0
        tz = timezone(self.spider.timezone)
        while days_previous <= max_days_previous:
            match_blobs = self.client.list_blobs(
                self.bucket_name,
                prefix=(
                    tz.localize(datetime.now()) - timedelta(days=days_previous)
                ).strftime(self.feed_prefix),
            )
            spider_blobs = [
                blob for blob in match_blobs if f"{self.spider.name}." in blob.name
            ]
            if len(spider_blobs) > 0:
                break
            days_previous += 1

        if len(spider_blobs) == 0:
            return []
        blob = sorted(spider_blobs, key=attrgetter("name"))[-1]
        feed_text = self.bucket.blob(blob.name).download_as_bytes().decode("utf-8")
        return [json.loads(line) for line in feed_text.split("\n") if line.strip()]
