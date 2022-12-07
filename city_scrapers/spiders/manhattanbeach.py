from city_scrapers.spiders.granicus import GranicusSpider


class ManhattanbeachSpider(GranicusSpider):
    name = "manhattanbeach"
    agency = "Manhattan Beach"
    sub_agency = "Planning Commission"
    start_urls = ["https://manhattanbeach.granicus.com/ViewPublisher.php?view_id=7"]
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
