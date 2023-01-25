from city_scrapers.spiders.granicus import GranicusSpider


class ManhattanbeachSpider(GranicusSpider):
    name = "manhattanbeach"
    agency = "Manhattan Beach"
    sub_agency = "City"
    start_urls = [
        # Planning Commission
        "https://manhattanbeach.granicus.com/ViewPublisher.php?view_id=7",
        # City Council
        "https://manhattanbeach.granicus.com/ViewPublisher.php?view_id=4",
    ]
    location = {
        "name": "",
        "address": "City Council Chambers "
        "1400 Highland Avenue, Manhattan Beach, CA 90266",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(
            self.name,
            self.agency,
            self.sub_agency,
            self.location,
            ["sortable"],
            *args,
            **kwargs,
        )
