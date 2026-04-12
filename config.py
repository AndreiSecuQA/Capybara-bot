import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8630601890:AAGcL-2ey6PbNBB8E_hraHei20SKEwfuWAs")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Use /data/capybara.db on Railway (volume mount), local file in dev
DATABASE_PATH = os.getenv("DATABASE_PATH", "capybara.db")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Bucharest")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Dev Agent config
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "AndreiSecuQA/Capybara-bot")
