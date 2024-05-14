import os
from pathlib import Path
from dotenv import load_dotenv

def get_raw_path():
    load_dotenv()

    current_dir = Path.cwd()
    data_dir = str(os.getenv('DATA_DIR'))
    raw_data_dir = str(os.getenv('RAW_DATA'))

    data_dir_path = current_dir.parent / data_dir
    
    return data_dir_path / raw_data_dir

print(get_raw_path())