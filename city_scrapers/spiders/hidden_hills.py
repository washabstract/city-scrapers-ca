from city_scrapers.spiders.granicus import GranicusSpider


class HiddenHillsSpider(GranicusSpider):
    name = "hidden_hills"
    agency = "Los Angeles"
    sub_agency = "Hidden Hills"
    start_urls = ["https://hiddenhillscity.granicus.com/ViewPublisher.php?view_id=1"]
    location = {"name": "", "address": "6165 Spring Valley Rd, Hidden Hills, CA 91302"}

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
