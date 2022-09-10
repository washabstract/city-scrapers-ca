from re import sub
import psycopg2
from flatdict import FlatDict

class PostgresAgencyPipeline:
    """
    Creates the appropriate agency hierarchies.
    """

    def __init__(self, host, user, password, database):
        self.postgres_host = host
        self.postgres_user = user
        self.postgres_password = password
        self.postgres_database = database
        self.hierarchy_count = {} # Format Eg. {"Los Angeles/World Airports/Meeting Name": 2}
        self.delimiter = "/"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("POSTGRES_HOST"),
            user=crawler.settings.get("POSTGRES_USER"),
            password=crawler.settings.get("POSTGRES_PASSWORD"),
            database=crawler.settings.get("POSTGRES_DATABASE"),
        )

    def get_agency_hierarchy(self, flatten=True):

        def get_sub_agencies(agency):
            # query to get the child agencies
            query = "SELECT * FROM agency WHERE parent_agency_id = %s;"
            # (id, name, parent_agency_id)
            hier = {"id": agency[0]}
            (sub_agencies, e) = self.sql_query(query, [agency[0]])
            if e:
                raise (e)
            
            for sub_agency in sub_agencies:
                hier[sub_agency[1]] = {
                    "id": sub_agency[0],
                    **get_sub_agencies(sub_agency)
                }
            
            return hier

        # query to get parent agencies
        query = "SELECT * FROM agency WHERE parent_agency_id IS NULL;"
        (parent_agencies, e) = self.sql_query(query)
        if e:
            raise (e)
        
        # Building hierarchy
        hierarchy = {}
        for parent_agency in parent_agencies:
            hierarchy[parent_agency[1]] = get_sub_agencies(parent_agency)
                
        if flatten:
            hierarchy = FlatDict(hierarchy, delimiter="/")
        
        return hierarchy

    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            host=self.postgres_host,
            user=self.postgres_user,
            password=self.postgres_password,
            dbname=self.postgres_database,
        )
        
        # Agency table
        (_, e) = self.sql_query("SELECT * FROM agency;")
        if type(e) is psycopg2.errors.UndefinedTable:
            query = (
                "CREATE TABLE agency ( "
                "id SERIAL PRIMARY KEY, "
                "name VARCHAR(255) NOT NULL, "
                "parent_agency_id BIGINT REFERENCES agency(id)"
                ");"
            )
            (_, e) = self.sql_query(query)
            if e:
                raise (e)
        elif e:
            raise (e)
        
        self.agency_hierarchy = self.get_agency_hierarchy()

    def process_item(self, item, spider):
        agency = item["extras"]["cityscrapers.org/agency"]
        sub_agency = item["extras"]["cityscrapers.org/sub_agency"]
        meeting_name = item["name"]

        full_path = [agency, sub_agency, meeting_name]
        full_path = [path for path in full_path if path != ""]
        full_path = self.delimiter.join(full_path)

        # Adding the frequencies
        if full_path in self.hierarchy_count:
            self.hierarchy_count[full_path] += 1
        else:
            self.hierarchy_count[full_path] = 1
        
        return item

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
    
    def get_or_create_agency(self, name, parent_agency_id):
        # Convert get or create
        if parent_agency_id is None:
            query = "SELECT id FROM agency WHERE name = %s AND parent_agency_id is NULL;"
            (records, e) = self.sql_query(query, (name,))
        else:    
            query = "SELECT id FROM agency WHERE name = %s AND parent_agency_id = %s;"
            (records, e) = self.sql_query(query, (name, parent_agency_id))
        
        if e:
            raise (e)
        
        if len(records) > 0:
            agency_id = records[0][0]
            return agency_id

        query = "INSERT INTO agency(name, parent_agency_id) VALUES (%s, %s) RETURNING id;"
        (records, e) = self.sql_query(query, (name, parent_agency_id))
        if e:
            raise (e)

        # Returning the id of the agency that was just created
        agency_id = records[0][0]
        return agency_id

    def close_spider(self, spider):
        agencies_created = {}

        # Here we can actually create create the agencies
        for full_path, count in self.hierarchy_count.items():
            # Resetting the parent agency
            parent_agency_id = None
            path_added = []
            agencies_path_list = full_path.split(self.delimiter)
            # The list depth will be used to determine if we will compare use the count
            list_depth = len(agencies_path_list) - 1

            for index, agency_name in enumerate(agencies_path_list):
                    path_to_add = ""
                    if index == list_depth:
                        if count > 1:
                            # Create the final sub agency of the hierarchy
                            path_to_add = agency_name
                            parent_agency_id = self.get_or_create_agency(agency_name, parent_agency_id)
                        else:
                            # Create the Other branch
                            path_to_add = "Other"
                            parent_agency_id = self.get_or_create_agency(path_to_add, parent_agency_id)
                    else:
                        # Create the agency and capture the parent_agency_id
                        path_to_add = agency_name
                        parent_agency_id = self.get_or_create_agency(agency_name, parent_agency_id)

                    # Adding to the list of the agencies that have been created
                    path_added.append(path_to_add)
                    agencies_created[self.delimiter.join(path_added)] = parent_agency_id
        
        # Finally closing the connection
        self.conn.close()

class PostgresPipeline:
    def __init__(self, host, user, password, database):
        self.postgres_host = host
        self.postgres_user = user
        self.postgres_password = password
        self.postgres_database = database
        self.delimiter = "/"

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
        
        # Agency capturing the hierarchy
        self.agency_hierarchy = self.get_agency_hierarchy()
        
        # Meeting table
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
                "agency_id BIGINT NOT NULL REFERENCES agency(id) DEFERRABLE INITIALLY DEFERRED, "
                "created TIMESTAMPTZ, "
                "updated TIMESTAMPTZ "
                ");"
            )
            (_, e) = self.sql_query(query)
            if e:
                raise (e)
        elif e:
            raise (e)
        
        # Link table
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
        
    def get_agency_hierarchy(self, flatten=True):

        def get_sub_agencies(agency):
            # query to get the child agencies
            query = "SELECT * FROM agency WHERE parent_agency_id = %s;"
            # (id, name, parent_agency_id)
            hier = {"id": agency[0]}
            (sub_agencies, e) = self.sql_query(query, [agency[0]])
            if e:
                raise (e)
            
            for sub_agency in sub_agencies:
                hier[sub_agency[1]] = {
                    "id": sub_agency[0],
                    **get_sub_agencies(sub_agency)
                }
            
            return hier

        # query to get parent agencies
        query = "SELECT * FROM agency WHERE parent_agency_id IS NULL;"
        (parent_agencies, e) = self.sql_query(query)
        if e:
            raise (e)
        
        # Building hierarchy
        hierarchy = {}
        for parent_agency in parent_agencies:
            hierarchy[parent_agency[1]] = get_sub_agencies(parent_agency)
                
        if flatten:
            hierarchy = FlatDict(hierarchy, delimiter="/")
        
        return hierarchy
        
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
        # Building the agency path
        agency = item["extras"]["cityscrapers.org/agency"]
        sub_agency = item["extras"]["cityscrapers.org/sub_agency"]
        meeting_name = item["name"]

        full_path = [agency, sub_agency, meeting_name, "id"]
        full_path = [path for path in full_path if path != ""]
        full_path = self.delimiter.join(full_path)

        full_path_other = [agency, sub_agency, meeting_name, "Other", "id"]
        full_path_other = [path for path in full_path_other if path != ""]
        full_path_other = self.delimiter.join(full_path_other)
        agency_id = None

        # checking if it exists
        if full_path in self.agency_hierarchy:
            agency_id = self.agency_hierarchy[full_path]
        elif full_path_other in self.agency_hierarchy:
            # Can link to the other agency
            agency_id = self.agency_hierarchy[full_path]
        else:
            print("Path:", full_path)
            print("Other Path:", full_path_other)
            raise Exception("Agency does not exist")

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
            agency_id,
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
                "location_url, agency_id, created, updated "
                ") VALUES ("
                "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
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
                "location_url = %s, agency_id = %s, created = %s, updated = %s "
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
                agency_id,
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
