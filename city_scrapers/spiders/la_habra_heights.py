from city_scrapers.spiders.granicus import GranicusSpider


class LaHabraHeightsSpider(GranicusSpider):
    name = "la_habra_heights"
    agency = "La Habra Heights"
    sub_agency = "City"
    start_urls = ["https://la-habra-heights.granicus.com/ViewPublisher.php?view_id=4"]

    location = {
        "name": "",
        "address": "1225 North Hacienda Road, La Habra Heights, California 90631",
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
