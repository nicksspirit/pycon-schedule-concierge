import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
BASE_EVENT_URL = "https://us.pycon.org/"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)