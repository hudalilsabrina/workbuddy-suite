#!/usr/bin/env python3
"""WorkBuddy Automation Suite - GitHub OAuth Integration & Credit Harvester CLI."""

import sys
import os
import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import rich.box as box

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from src.config import BASE_URL, LOGIN_URL, ACCOUNTS_JSON, TOKENS_TXT, ACCOUNTS_INPUT
from src.browser import login_workbuddy_via_github
from src.client import WorkBuddyClient

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def print_banner():
    content = Text.assemble(
        Text("WORKBUDDY AUTOMATION SUITE", style="bold cyan"), "\n",
        Text("Tencent WorkBuddy • GitHub OAuth Harvester • Welcome Credits Farm", style="dim"), "\n\n",
        Text(f"Target Portal   : {LOGIN_URL}", style="cyan"), "\n",
        Text(f"Storage Database: {ACCOUNTS_JSON}", style="bright_black"),
    )
    console.print(Panel(content, box=box.ROUNDED, border_style="cyan"))


def load_state() -> dict:
    if ACCOUNTS_JSON.exists():
        try:
            with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_state(state: dict):
    with open(ACCOUNTS_JSON, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


async def cmd_login(args):
    print_banner()

    user = args.user
    pwd = args.password
    cookie = args.cookie
    totp = args.totp

    if not cookie and not (user and pwd):
        if Path(ACCOUNTS_INPUT).exists():
            console.print(f"[cyan]Reading accounts from {ACCOUNTS_INPUT}...[/]")
            with open(ACCOUNTS_INPUT, "r") as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            if lines:
                parts = lines[0].split("----") if "----" in lines[0] else lines[0].split(":")
                user = parts[0]
                pwd = parts[1] if len(parts) > 1 else ""
                totp = parts[2] if len(parts) > 2 else None
        else:
            console.print("[bold red]Error: Silakan tentukan --user & --password, atau --cookie user_session, atau buat file accounts.txt.[/]")
            return

    identifier = user or "cookie_session"
    console.print(f"[bold cyan]Starting GitHub OAuth flow for: {identifier}...[/]\n")

    res = await login_workbuddy_via_github(
        gh_username=user,
        gh_password=pwd,
        gh_session_cookie=cookie,
        totp_secret=totp,
        headless=not args.headed
    )

    if not res.get("success"):
        console.print(f"[bold red]✗ Login failed: {res.get('error')}[/]")
        return

    cookies = res.get("cookies", {})
    console.print(f"[bold green]✓ Berhasil login ke WorkBuddy! ({len(cookies)} cookies diperoleh)[/]")

    # Check resources / credits
    client = WorkBuddyClient(cookies)
    resources = client.get_user_resources()
    quota = client.get_cloudagent_quota()

    credits = 0
    if isinstance(resources, dict) and "data" in resources:
        res_list = resources["data"].get("resources", [])
        for r in res_list:
            credits += r.get("remaining", 0)

    console.print(f"[bold green]🎉 Total Credits Tersedia: {credits} credits[/]")

    # Save to state
    state = load_state()
    state[identifier] = {
        "account": identifier,
        "cookies": cookies,
        "credits": credits,
        "resources": resources,
        "quota": quota,
        "created_at": datetime.now().isoformat()
    }
    save_state(state)
    console.print(f"[dim]Data akun berhasil disimpan ke {ACCOUNTS_JSON}[/]\n")


def cmd_list(args):
    print_banner()
    state = load_state()
    if not state:
        console.print("[yellow]Belum ada akun WorkBuddy yang tersimpan.[/]")
        return

    table = Table(title="Akun WorkBuddy Tersimpan", box=box.ROUNDED)
    table.add_column("No", justify="right", style="dim")
    table.add_column("Account / Identifier", style="cyan")
    table.add_column("Credits", justify="center", style="green")
    table.add_column("Cookies Count", justify="center")
    table.add_column("Registered At", style="dim")

    for i, (k, v) in enumerate(state.items(), 1):
        table.add_row(
            str(i),
            k,
            str(v.get("credits", 0)),
            str(len(v.get("cookies", {}))),
            v.get("created_at", "-")[:19]
        )

    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="WorkBuddy GitHub OAuth Harvester")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # login
    p_log = subparsers.add_parser("login", help="Authenticate with WorkBuddy via GitHub OAuth")
    p_log.add_argument("-u", "--user", help="GitHub username / email")
    p_log.add_argument("-p", "--password", help="GitHub password")
    p_log.add_argument("-c", "--cookie", help="GitHub user_session cookie directly")
    p_log.add_argument("-t", "--totp", help="GitHub 2FA base32 secret")
    p_log.add_argument("--headed", action="store_true", help="Run browser in headed mode for visual debugging")

    # list
    subparsers.add_parser("list", aliases=["ls"], help="List harvested WorkBuddy accounts and credits")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "login":
        asyncio.run(cmd_login(args))
    elif args.subcommand in ("list", "ls"):
        cmd_list(args)


if __name__ == "__main__":
    main()
