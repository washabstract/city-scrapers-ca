from city_scrapers.spiders.granicus import GranicusSpider


class RollingHillsEstatesSpider(GranicusSpider):
    name = "rolling_hills_estates"
    agency = "Rolling Hills Estates"
    sub_agency = "Planning Commission"
    start_urls = [
        "https://rollinghillsestatesca.granicus.com/ViewPublisher.php?view_id=1"
    ]
    location = {
        "name": "",
        "address": "4045 PALOS VERDES DRIVE NORTH, ROLLING HILLS ESTATES, CA 90274",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(
            self.name,
            self.agency,
            self.sub_agency,
            self.location,
            None,
            *args,
            **kwargs,
        )
