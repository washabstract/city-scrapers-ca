from city_scrapers.spiders.granicus import GranicusSpider


class WestLakeVillageSpider(GranicusSpider):
    name = "west_lake_village"
    agency = "West Lake Village"
    sub_agency = "City Council"
    start_urls = ["https://westlakevillage.granicus.com/viewpublisher.php?view_id=8"]
    location = {
        "title": "City Council Chambers",
        "href": "31200 Oak Crest Dr, Westlake Village, CA 91361, USA",
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
