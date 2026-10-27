"""Browser automation for WorkBuddy GitHub OAuth integration using Camoufox."""

import asyncio
import logging
from typing import Dict, Any, Optional

from camoufox.async_api import AsyncCamoufox
from src.config import BASE_URL, LOGIN_URL, GITHUB_BROKER_URL, HEADLESS, TIMEOUT

logger = logging.getLogger("workbuddy.browser")


async def login_workbuddy_via_github(
    gh_username: Optional[str] = None,
    gh_password: Optional[str] = None,
    gh_session_cookie: Optional[str] = None,
    totp_secret: Optional[str] = None,
    headless: bool = HEADLESS
) -> Dict[str, Any]:
    """Automates WorkBuddy signup / login through GitHub OAuth."""
    logger.info("Initializing Camoufox for WorkBuddy GitHub OAuth...")

    async with AsyncCamoufox(headless=headless) as browser:
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Pre-authenticate GitHub if user_session cookie is provided
        if gh_session_cookie:
            logger.info("Injecting GitHub user_session cookie...")
            await context.add_cookies([{
                "name": "user_session",
                "value": gh_session_cookie,
                "domain": ".github.com",
                "path": "/",
                "secure": True,
                "httpOnly": True
            }])

        # If username and password provided without pre-auth cookie, log in to GitHub first
        elif gh_username and gh_password:
            logger.info(f"Logging in to GitHub as {gh_username}...")
            await page.goto("https://github.com/login", wait_until="domcontentloaded")
            await asyncio.sleep(2)

            await page.fill('input[name="login"]', gh_username)
            await page.fill('input[name="password"]', gh_password)
            await page.click('input[type="submit"][name="commit"]')
            await asyncio.sleep(4)

            # Check for 2FA or device OTP
            current_url = page.url
            if "two-factor" in current_url or "sessions/two-factor" in current_url:
                if totp_secret:
                    from src.totp import generate_totp
                    code = generate_totp(totp_secret)
                    logger.info(f"Submitting 2FA TOTP code: {code}...")
                    await page.fill('input[name="otp"], input[name="app_totp"]', code)
                    await asyncio.sleep(3)
                else:
                    return {
                        "success": False,
                        "error": "GitHub 2FA / Device Verification required. Please provide totp_secret or pre-authenticated user_session cookie."
                    }

        # Step 2: Navigate to WorkBuddy GitHub OAuth Broker
        logger.info(f"Navigating to WorkBuddy GitHub Broker: {GITHUB_BROKER_URL}...")
        try:
            await page.goto(GITHUB_BROKER_URL, wait_until="networkidle", timeout=TIMEOUT * 1000)
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Navigation error: {e}")

        # Step 3: Check if on GitHub consent / authorization page
        if "github.com/login/oauth/authorize" in page.url or "github.com/login" in page.url:
            logger.info("On GitHub OAuth authorization page...")

            # If redirected to GitHub login (e.g. session not persisted)
            if "github.com/login" in page.url and gh_username and gh_password:
                login_input = page.locator('input[name="login"]')
                if await login_input.count() > 0:
                    await login_input.fill(gh_username)
                    await page.fill('input[name="password"]', gh_password)
                    await page.click('input[type="submit"][name="commit"]')
                    await asyncio.sleep(4)

            # Look for Authorize button
            authorize_btn = page.locator('button[name="authorize"], input[name="authorize"], #js-oauth-authorize-btn, button:has-text("Authorize")')
            if await authorize_btn.count() > 0:
                logger.info("Clicking 'Authorize WorkBuddy' on GitHub...")
                await authorize_btn.first.click()
                await asyncio.sleep(5)

        # Step 4: Wait for redirect back to WorkBuddy
        logger.info("Waiting for callback redirect to WorkBuddy...")
        for _ in range(15):
            await asyncio.sleep(1)
            current_url = page.url
            if "workbuddy.ai" in current_url and ("select" in current_url or "app" in current_url or current_url.endswith("/")):
                logger.info(f"Successfully redirected to WorkBuddy: {current_url}")
                break

        # Step 5: Extract tokens, cookies, and local storage
        cookies = await context.cookies()
        storage = await page.evaluate("""() => {
            const data = {};
            for (let i = 0; i < localStorage.length; i++) {
                const k = localStorage.key(i);
                data[k] = localStorage.getItem(k);
            }
            return data;
        }""")

        cb_cookies = {c["name"]: c["value"] for c in cookies if "workbuddy.ai" in c.get("domain", "")}

        return {
            "success": True,
            "final_url": page.url,
            "cookies": cb_cookies,
            "storage_keys": list(storage.keys()),
            "localStorage": storage
        }
