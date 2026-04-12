import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8630601890:AAGcL-2ey6PbNBB8E_hraHei20SKEwfuWAs")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# Use /data/capybara.db on Railway (volume mount), local file in dev
DATABASE_PATH = os.getenv("DATABASE_PATH", "capybara.db")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Bucharest")
