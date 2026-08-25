import os

from dotenv import load_dotenv


load_dotenv()


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