import json
from datetime import datetime, timedelta
from operator import itemgetter

from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError


class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return "[options]"

    def short_desc(self):
        return "Combine all recent feeds into latest.json and upcoming.json"

    def run(self, args, opts):
        storages = self.settings.get("FEED_STORAGES", {})
        if "gcs" in storages:
            self.combine_gcs()
        else:
            raise UsageError(
                "'gcs' must be in FEED_STORAGES to combine past feeds"
            )

    def combine_gcs(self):
        from google.cloud import storage

        bucket_name = self.settings.get("GCS_BUCKET")
        feed_prefix = self.settings.get("CITY_SCRAPERS_DIFF_FEED_PREFIX", "%Y/%m/%d")
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        max_days_previous = 3
        days_previous = 0
        prefix_blobs = []
        while days_previous <= max_days_previous:
            prefix_blobs = client.list_blobs(
                bucket,
                prefix=(datetime.now() - timedelta(days=days_previous)).strftime(
                    feed_prefix
                ),
            )
            prefix_blobs = [blob for blob in prefix_blobs]
            if len(prefix_blobs) > 0:
                break
            days_previous += 1

        meetings = []
        for blob in prefix_blobs:
            feed_text = blob.download_as_bytes().decode("utf-8")
            meetings.extend(
                [json.loads(line) for line in feed_text.split("\n") if line.strip()]
            )
            # Copy latest results for each spider
            spider_name = blob.name.split("/")[-1]
            bucket.copy_blob(blob, bucket, new_name=spider_name)
        meetings = sorted(meetings, key=itemgetter(self.start_key))
        yesterday_iso = (datetime.now() - timedelta(days=1)).isoformat()[:19]
        upcoming = [
            meeting
            for meeting in meetings
            if meeting[self.start_key][:19] > yesterday_iso
        ]
        
        new_meetings_blob = bucket.blob("latest.json")
        new_meetings_blob.upload_from_string(
            "\n".join([json.dumps(meeting) for meeting in meetings]).encode()
        )
        new_upcoming_blob = bucket.blob("upcoming.json")
        new_upcoming_blob.upload_from_string(
            "\n".join([json.dumps(meeting) for meeting in upcoming]).encode()
        )

    def get_spider_paths(self, path_list):
        """Get a list of the most recent scraper results for each spider"""
        spider_paths = []
        for spider in self.crawler_process.spider_loader.list():
            all_spider_paths = [p for p in path_list if f"{spider}." in p]
            if len(all_spider_paths) > 0:
                spider_paths.append(sorted(all_spider_paths)[-1])
        return spider_paths

    @property
    def start_key(self):
        pipelines = self.settings.get("ITEM_PIPELINES", {})
        if "city_scrapers_core.pipelines.OpenCivicDataPipeline" in pipelines:
            return "start_time"
        return "start"
