import os
import pickle
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv, dotenv_values
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def test():
    print(__file__)

# Load .env file
env_config = dotenv_values()

