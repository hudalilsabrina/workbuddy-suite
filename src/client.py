"""WorkBuddy API client for inspecting quota, credits, and account status."""

import urllib.request
import json
import logging
from typing import Dict, Any, Optional

from src.config import BASE_URL

logger = logging.getLogger("workbuddy.client")


class WorkBuddyClient:
    def __init__(self, cookies: Dict[str, str], token: Optional[str] = None):
        self.cookies = cookies
        self.token = token
        self.cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])

    def _headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Cookie": self.cookie_header,
            "x-product": "workbuddy",
            "x-requested-with": "XMLHttpRequest"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_user_resources(self) -> Dict[str, Any]:
        """Fetches user balance, welcome credits, and active subscriptions."""
        url = f"{BASE_URL}/billing/meter/get-user-resource"
        req = urllib.request.Request(url, data=b"{}", headers=self._headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "message": e.read().decode()}
        except Exception as e:
            return {"error": str(e)}

    def get_cloudagent_quota(self) -> Dict[str, Any]:
        """Fetches automated task & cloud agent quota limits."""
        url = f"{BASE_URL}/v2/user/cloudagent/quota"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "message": e.read().decode()}
        except Exception as e:
            return {"error": str(e)}
