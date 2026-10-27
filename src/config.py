"""Configuration loader for WorkBuddy Suite."""

from pathlib import Path
import tomllib

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.toml"

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "rb") as f:
            return tomllib.load(f)
    return {}

CONFIG = load_config()

BASE_URL = CONFIG.get("app", {}).get("base_url", "https://www.workbuddy.ai")
LOGIN_URL = CONFIG.get("app", {}).get("login_url", "https://www.workbuddy.ai/login/?platform=website&state=2&redirect_uri=https%3A%2F%2Fwww.workbuddy.ai%2F&product=workbuddy")
GITHUB_BROKER_URL = CONFIG.get("app", {}).get("github_broker_url", "https://www.workbuddy.ai/auth/realms/copilot/broker/github/login?client_id=console&product=workbuddy")
AUTH_REALM_URL = CONFIG.get("app", {}).get("auth_realm_url", "https://www.workbuddy.ai/auth/realms/copilot")

HEADLESS = CONFIG.get("browser", {}).get("headless", True)
TIMEOUT = CONFIG.get("browser", {}).get("timeout", 35)

DATA_DIR = ROOT_DIR / CONFIG.get("storage", {}).get("data_dir", "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNTS_JSON = ROOT_DIR / CONFIG.get("storage", {}).get("accounts_json", "data/accounts.json")
TOKENS_TXT = ROOT_DIR / CONFIG.get("storage", {}).get("tokens_txt", "data/tokens.txt")
ACCOUNTS_INPUT = ROOT_DIR / CONFIG.get("storage", {}).get("accounts_input", "accounts.txt")
