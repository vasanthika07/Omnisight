import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve repository root
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(ROOT_DIR / ".env")

# Core Paths
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
PATCHES_DIR = ARTIFACTS_DIR / "patches"
TEST_APP_DIR = ROOT_DIR / "test-app"
DB_PATH = ROOT_DIR / "backend" / "storage" / "omnisight.sqlite"

# Ensure runtime directories exist
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
PATCHES_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Provider and API keys
VISION_PROVIDER = os.getenv("VISION_PROVIDER", "auto").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "").strip()

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "127.0.0.1")
TEST_APP_PORT = int(os.getenv("TEST_APP_PORT", "5174"))

# Standard QA Viewports
VIEWPORTS = {
    "mobile": {"width": 375, "height": 812, "name": "iPhone 14 / Mobile"},
    "tablet": {"width": 768, "height": 1024, "name": "iPad Mini / Tablet"},
    "desktop": {"width": 1440, "height": 900, "name": "MacBook / Desktop Standard"}
}
