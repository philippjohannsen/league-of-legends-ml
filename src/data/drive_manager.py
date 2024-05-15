import os
import pickle
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Load .env file
load_dotenv()

# Get environment variables
credentials = str(os.getenv('CREDENTIALS'))
token = str(os.getenv('TOKEN'))
drive_files = str(os.getenv('DRIVE_FILES'))
metadata = str(os.getenv('METADATA'))
data_dir = str(os.getenv('DATA_DIR'))
raw_dir = str(os.getenv('RAW_DATA'))
scope = os.getenv('SCOPES')

# Define paths
drive_files_path = os.path.abspath(drive_files)
token_path = os.path.join(drive_files_path, token)
credentials_path = os.path.join(drive_files_path, credentials)
metadata_path = os.path.join(drive_files, metadata)

data_dir_path = os.path.abspath(data_dir)
raw_dir_path = os.path.join(data_dir_path, raw_dir)

# Functions for reading and writing metadata - used for checking if data is up-to-date
def load_metadata():
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    else:
        return {}

def write_metadata(data):
    with open(metadata_path, 'w') as f:
        json.dump(data, f)

# Authenticate Google Drive
def auth():
    creds = None

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, [scope])
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

# Download files from Google Drive
def drive_download(google_drive_service, files_to_download):
    for file_name, details in files_to_download.items():
        file_path = os.path.join(raw_dir_path, file_name)
        file_id = details['id']
        print(f"Downloading {file_name}...")
        # from https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaIoBaseDownload-class.html
        request = google_drive_service.files().get_media(fileId=file_id)
        with open(file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloaded {file_name} {int(status.progress() * 100)}% complete.")
    print(f"All files downloaded successfully to {os.path.dirname(file_path)}.")


# Manage Google Drive files in local storage (data/raw/)
def drive(folder_id):
    # Establish connection to Google Drive folder
    creds = auth()
    google_drive_service = build('drive', 'v3', credentials=creds)
    query = f"'{folder_id}' in parents and trashed = false"
    results = google_drive_service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
    drive_data = results.get('files', [])

    if not drive_data:
        print("No files found in the Google Drive folder.")
        return

    # Load local metadata
    metadata = load_metadata()

    # Get a list of files in the local data storage
    local_data = [os.fsdecode(file) for file in os.listdir(raw_dir_path) if os.fsdecode(file).endswith('.csv')]

    # Create a dictionary with files in the Google Drive folder and get file_id and modifiedTime (used for checking if local data is up-to-date)
    drive_files_dict = {file['name']: {'id': file['id'], 'modifiedTime': file['modifiedTime']} for file in drive_data}

    # Create a dictionary of files to download based on metadata and local file storage info
    files_to_download = {}
    for file_name, file_info in drive_files_dict.items():
        file_modified_time = file_info['modifiedTime']
        if file_name not in local_data or metadata.get(file_name, '1970-01-01T00:00:00.000Z') < file_modified_time:
            files_to_download[file_name] = {'id': file_info['id'], 'name': file_name}

    # If there are files to download, download them
    if files_to_download:
        print("The following files are missing or outdated:")
        for file_name in files_to_download:
            print(f"{file_name} (Last modified: {drive_files_dict[file_name]['modifiedTime']})")
        print("Downloading updated or missing files...")
        drive_download(google_drive_service, files_to_download)

        # Update metadata after downloading
        for file_name in files_to_download:
            metadata[file_name] = drive_files_dict[file_name]['modifiedTime']
        write_metadata(metadata)
    else:
        print("No updates found. All files are up-to-date.")

