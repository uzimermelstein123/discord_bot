import requests
from dotenv import load_dotenv
import os

load_dotenv()
CANVAS_API_KEY = os.getenv("CANVAS_API_KEY")


response = requests.get(
    "https://REPLACE_ME/api/v1/applicants",
    headers={"Authorization":CANVAS_API_KEY,"Accept":"*/*"},
)

data = response.json()