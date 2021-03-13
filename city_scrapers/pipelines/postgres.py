class PostgresPipeline:
    """Implements :class:`Pipeline` for PostgreSQL"""

    def __init__(self):
        import psycopg2

        self.conn = psycopg2.connect(
            user="pi", dbname="cg_scraping", host="/var/run/postgresql/"
        )
        # TODO: Make sure table exists before processing items

    def process_item(self, item, spider):
        cur = self.conn.cursor()

        cur.execute(
            """
                insert into meetings ( schema )
                values ( values );
                """,
            [
                item["value"],
            ],
        )
        self.conn.commit()
        return item


# MEETING
# id = PK
# title = string
# description = long string
# classification = string
# status = string
# start = datetime
# end = datetime
# all_day = bool
# time_notes = long string
# location_name = long string
# location_address = long string
# location_url = string (URL)
# links = FK->Links
# source = string (URL)

# LINK
# id = PK
# title = string
# href = string (URL)
# raw_text = long string

# MEETING
# id = ocd_event["_id"]
# title = ocd_event["name"]
# description = ocd_event["description"]
# classification = ocd_event["classification"]
# status = ocd_event["status"]
# start = ocd_event["start_time"]
# end = ocd_event["end_zone"]
# timezone = ocd_event["timezone"]
# all_day = ocd_event["all_day"]
# time_notes = ocd_event["extras"]["cityscrapers.org/time_notes"]
# location_name = ocd_event["location"]["name"]
# location_address = ocd_event["extras"]["cityscrapers.org/address"]
# location_url = ocd_event["location"]["url"]
# links = FK->Links
# agency = ocd_event["extras"]["cityscrapers.org/agency"]

# LINK
# id = PK
# note = ocd_event["links"][x]["note"]
# url = ocd_event["links"][x]["url"]
# raw_text = ocd_event["links"][x]["raw_text"]
