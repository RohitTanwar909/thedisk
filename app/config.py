import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
