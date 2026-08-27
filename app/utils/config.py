import os

from dotenv import load_dotenv


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "qwen2.5:7b-instruct",
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "3")
)

INPUT_FILE = os.getenv(
    "INPUT_FILE",
    "inputs/input_requests.csv",
)

OUTPUT_FILE = os.getenv(
    "OUTPUT_FILE",
    "results/output.json",
)

REPORT_FILE = os.getenv(
    "REPORT_FILE",
    "results/report.md",
)

GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE",
    "credentials.json",
)

GOOGLE_SPREADSHEET_ID = os.getenv(
    "GOOGLE_SPREADSHEET_ID",
)

GOOGLE_WORKSHEET_NAME = os.getenv(
    "GOOGLE_WORKSHEET_NAME",
    "Requests",
)