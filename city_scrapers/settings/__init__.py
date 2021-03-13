import logging
import os

path = "{}/google-cloud-storage-credentials.json".format(os.getcwd())

try:
    credentials_content = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
except KeyError:
    logging.warning("GCS credentials not found! creating new path.")
    credentials_content = False

if not os.path.exists(credentials_content):
    with open(path, "w") as f:
        f.write(credentials_content)
    logging.warning("New path to credentials: %s" % path)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
