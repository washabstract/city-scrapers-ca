import psycopg2


class PostgresPipeline:
    def __init__(self, host, user, password, database):
        self.postgres_host = host
        self.postgres_user = user
        self.postgres_password = password
        self.postgres_database = database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("POSTGRES_HOST"),
            user=crawler.settings.get("POSTGRES_USER"),
            password=crawler.settings.get("POSTGRES_PASSWORD"),
            database=crawler.settings.get("POSTGRES_DATABASE"),
        )

    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            host=self.postgres_host,
            user=self.postgres_user,
            password=self.postgres_password,
            dbname=self.postgres_database,
        )

        (_, e) = self.sql_query("SELECT * FROM meeting;")
        if type(e) is psycopg2.errors.UndefinedTable:
            query = (
                "CREATE TABLE meeting ( "
                "id VARCHAR(255) PRIMARY KEY, "
                "ocd_id VARCHAR(255) NOT NULL, "
                "name VARCHAR(255) NOT NULL, "
                "classification VARCHAR(255), "
                "description TEXT, "
                "status VARCHAR(255), "
                "start_tz TIMESTAMPTZ, "
                "end_tz TIMESTAMPTZ, "
                "timezone VARCHAR(255), "
                "all_day BOOLEAN, "
                "time_notes TEXT, "
                "location_name TEXT, "
                "location_address TEXT, "
                "location_url TEXT, "
                "agency VARCHAR(255), "
                "created TIMESTAMPTZ, "
                "updated TIMESTAMPTZ "
                ");"
            )
            (_, e) = self.sql_query(query)
            if e:
                raise (e)
        elif e:
            raise (e)

        (_, e) = self.sql_query("SELECT * FROM link;")
        if type(e) is psycopg2.errors.UndefinedTable:
            query = (
                "CREATE TABLE link ( "
                "id SERIAL PRIMARY KEY, "
                "meeting_id VARCHAR(255) REFERENCES meeting (id), "
                "note TEXT, "
                "url TEXT, "
                "raw_text TEXT"
                ");"
            )
            (_, e) = self.sql_query(query)
            if e:
                raise (e)
        elif e:
            raise (e)

    def close_spider(self, spider):
        self.conn.close()

    def sql_query(self, query, data=None):
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(query, data)
                except Exception as e:
                    self.conn.rollback()
                    return ([], e)
                else:
                    self.conn.commit()
                    try:
                        return (cursor.fetchall(), None)
                    except psycopg2.ProgrammingError:
                        return ([], None)

    def process_item(self, item, spider):
        data = (
            item["extras"]["cityscrapers.org/id"],
            item["_id"],
            item["name"],
            item["description"],
            item["classification"],
            item["status"],
            item["start_time"],
            item["end_time"],
            item["timezone"],
            item["all_day"],
            item["extras"]["cityscrapers.org/time_notes"],
            item["location"]["name"],
            item["location"]["url"],
            item["extras"]["cityscrapers.org/agency"],
            item["created_at"],
            item["updated_at"],
        )
        query = "SELECT * FROM meeting WHERE id=%s;"
        (records, e) = self.sql_query(query, (data[0],))
        if e:
            raise (e)
        if len(records) == 0:
            query = (
                "INSERT INTO meeting("
                "id, ocd_id, name, description, classification, status, start_tz, "
                "end_tz, timezone, all_day, time_notes, location_name, "
                "location_url, agency, created, updated "
                ") VALUES ("
                "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
                ");"
            )
            (_, e) = self.sql_query(query, data)
            if e:
                raise (e)
        else:
            query = (
                "UPDATE meeting SET "
                "ocd_id = %s, name = %s, description = %s, classification = %s, "
                "status = %s, start_tz = %s, end_tz = %s, timezone = %s, "
                "all_day = %s, time_notes = %s, location_name = %s, "
                "location_url = %s, agency = %s, created = %s, updated = %s "
                "WHERE id=%s"
            )
            data = (
                item["_id"],
                item["name"],
                item["description"],
                item["classification"],
                item["status"],
                item["start_time"],
                item["end_time"],
                item["timezone"],
                item["all_day"],
                item["extras"]["cityscrapers.org/time_notes"],
                item["location"]["name"],
                item["location"]["url"],
                item["extras"]["cityscrapers.org/agency"],
                item["created_at"],
                item["updated_at"],
                item["extras"]["cityscrapers.org/id"],
            )
            (_, e) = self.sql_query(query, data)
            if e:
                raise (e)
        for link in item["links"]:
            data = (
                item["extras"]["cityscrapers.org/id"],
                link["note"],
                link["url"],
                link.get("raw_text", ""),
            )
            query = "SELECT * FROM link WHERE meeting_id=%s AND url=%s;"
            (records, e) = self.sql_query(query, (data[0], data[2]))
            if e:
                raise (e)
            if len(records) == 0:
                query = (
                    "INSERT INTO link("
                    "meeting_id, note, url, raw_text"
                    ") VALUES ("
                    "%s, %s, %s, %s"
                    ");"
                )
                (_, e) = self.sql_query(query, data)
                if e:
                    raise (e)
            else:
                query = (
                    "UPDATE link SET note = %s, raw_text = %s"
                    "WHERE meeting_id=%s AND url=%s"
                )
                data = (
                    link["note"],
                    link.get("raw_text", ""),
                    item["extras"]["cityscrapers.org/id"],
                    link["url"],
                )
                (_, e) = self.sql_query(query, data)
                if e:
                    raise (e)
        return item


# MEETING
# id = string: item["extras"]["cityscrapers.org/id"]
# ocd_id = PK: ocd_event["_id"]
# title = string: ocd_event["name"]
# description = long string: ocd_event["description"]
# classification = string: ocd_event["classification"]
# status = string: ocd_event["status"]
# start_tz = datetime: ocd_event["start_time"]
# end_tz = datetime: ocd_event["end_zone"]
# timezone = string: ocd_event["timezone"]
# all_day = bool: ocd_event["all_day"]
# time_notes = long string: ocd_event["extras"]["cityscrapers.org/time_notes"]
# location_name = long string: ocd_event["location"]["name"]
# location_address = long string: ocd_event["extras"]["cityscrapers.org/address"]
# location_url = string (URL): ocd_event["location"]["url"]
# agency = string (URL): ocd_event["extras"]["cityscrapers.org/agency"]
# created = datetime: ocd_event["created_at"]
# updated = datetime: ocd_event["updated_at"]

# LINK
# id = PK
# meeting_id = PK
# note = string: ocd_event["links"][x]["note"]
# url = string (URL): ocd_event["links"][x]["url"]
# raw_text = long string: ocd_event["links"][x]["raw_text"]
