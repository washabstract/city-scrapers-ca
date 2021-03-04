from datetime import datetime

import pytz
from scrapy import Spider, signals
from scrapy.crawler import Crawler
from city_scrapers_core.extensions import StatusExtension

RUNNING = "running"
FAILING = "failing"
STATUS_COLOR_MAP = {RUNNING: "#44cc11", FAILING: "#cb2431"}
STATUS_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="144" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="a">
        <rect width="144" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#a)">
        <path fill="#555" d="M0 0h67v20H0z"/>
        <path fill="{color}" d="M67 0h77v20H67z"/>
        <path fill="url(#b)" d="M0 0h144v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
        <text x="345" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{status}</text>
        <text x="345" y="140" transform="scale(.1)">{status}</text>
        <text x="1045" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{date}</text>
        <text x="1045" y="140" transform="scale(.1)">{date}</text>
    </g>
</svg>
"""  # noqa


class GCSStatusExtension(StatusExtension):
    """Implements :class:`StatusExtension` for Google Cloud Storage"""

    def update_status_svg(self, spider: Spider, svg: str):
        """Implements writing templated status SVG to Google Cloud Storage
        :param spider: Spider with the status being tracked
        :param svg: Templated SVG string
        """

        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(
            self.crawler.settings.get("CITY_SCRAPERS_STATUS_BUCKET")
        )

        svg_blob = bucket.blob(f"{spider.name}.svg")
        svg_blob.upload_from_string(
            svg.encode(), content_type="image/svg+xml"
        )
