from __future__ import print_function
import os
import sys
import argparse

# from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# Builds empty argparse data to keep flow auth
argparser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser],
)
flags = argparser.parse_args(sys.argv[3:])


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES = "https://spreadsheets.google.com/feeds"
APPLICATION_NAME = "pyWeWork Drive"

cwd = os.path.dirname(__file__)
# Client App Credentials - Embed
CREDETIAL_DIR = os.path.join(cwd, "credentials")
CLIENT_SECRET_FILE = "client_secret.json"
CLIENT_SECRET_FILE = os.path.join(CREDETIAL_DIR, CLIENT_SECRET_FILE)

# User auth
CREDENTIAL_FILENAME = "pywework-auth.json"
home_dir = os.path.expanduser("~")
credential_dir = os.path.join(home_dir, ".credentials")
if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)

CREDENTIAL_PATH = os.path.join(credential_dir, CREDENTIAL_FILENAME)


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_path = os.path.join(CREDENTIAL_PATH)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        import sys

        print(sys.argv)
        credentials = tools.run_flow(flow, store, flags)

        print("Storing credentials to " + credential_path)
    return credentials
