import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


user_input = """add 5 and six, turn the result into uppercase letters, 
then tell me how's the weather in Toronto now, in celciius and 
Fareniheits. Also tell me who wrote Quran."""

Model_Name = "gpt-5.4-mini"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")