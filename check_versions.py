#!/usr/bin/env python3
"""Helper script to check bot versions in sibling repositories against addon configs."""

import os
import re
import yaml

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
ADDONS_DIR = os.path.join(REPO_ROOT, "addons")
PARENT_DIR = os.path.dirname(REPO_ROOT)

MAPPING = {
    "uptime": "deltachat_uptime",
    "telegram_bridge": "deltachat_telegram_bridge",
    "webpreview": "deltachat_webpreview",
    "bouncer": "deltachat_bouncer",
    "ntfy": "deltachat_ntfy",
    "youtube": "deltachat_yt",
    "username": "deltachat_username",
    "publisher": "deltachat_publish",
}

def main():
    print(f"{'Add-on':<20} {'Add-on Version':<18} {'Source Version':<18} {'Status'}")
    print("-" * 68)
    for addon_dir, bot_repo in MAPPING.items():
        cfg_path = os.path.join(ADDONS_DIR, addon_dir, "config.yaml")
        addon_ver = "N/A"
        if os.path.isfile(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                addon_ver = cfg.get("version", "N/A")

        src_bot_py = os.path.join(PARENT_DIR, bot_repo, "bot.py")
        src_ver = "N/A"
        if os.path.isfile(src_bot_py):
            with open(src_bot_py, "r", encoding="utf-8") as f:
                content = f.read()
                m = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
                if m:
                    src_ver = m.group(1)

        status = "✅ Synced" if addon_ver == src_ver else "⚠️ Diff"
        if src_ver == "N/A":
            status = "ℹ️ Source not found"
        print(f"{addon_dir:<20} {addon_ver:<18} {src_ver:<18} {status}")

if __name__ == "__main__":
    main()
