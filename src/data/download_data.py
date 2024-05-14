import os
from drive_manager import drive
from dotenv import load_dotenv


# Load .env file
load_dotenv()

# Get environment variables
drive_files = str(os.getenv('DRIVE_FILES'))
data_dir = str(os.getenv('DATA_DIR'))
raw_dir = str(os.getenv('RAW_DATA'))
elixir_drive = str(os.getenv('ELIXIR'))

# Define paths
drive_files_path = os.path.abspath(drive_files)
data_dir_path = os.path.abspath(data_dir)
raw_dir_path = os.path.join(data_dir_path, raw_dir)

if __name__ == '__main__':
    # Check if data directory exists. It is created if not
    if not os.path.exists(raw_dir_path):
        os.makedirs(raw_dir_path)
    
    if not os.path.exists(drive_files_path):
        os.makedirs(drive_files_path)
    
    # Download data from Google Drive
    drive(elixir_drive)


    