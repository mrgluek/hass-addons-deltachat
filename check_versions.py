#!/usr/bin/env python3
"""Helper script to check and sync bot versions in sibling repositories against addon configs."""

import argparse
import os
import re
import urllib.request
import urllib.error
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
    "yt": "deltachat_yt",
    "username": "deltachat_username",
    "publish": "deltachat_publish",
}

def extract_version_from_text(content: str) -> str:
    m = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if m:
        return m.group(1)
    return ""

def get_source_version(bot_repo: str) -> str:
    # 1. Local filesystem check
    bot_dir = os.path.join(PARENT_DIR, bot_repo)
    if os.path.isdir(bot_dir):
        bot_py = os.path.join(bot_dir, "bot.py")
        if os.path.isfile(bot_py):
            with open(bot_py, "r", encoding="utf-8") as f:
                ver = extract_version_from_text(f.read())
                if ver:
                    return ver
        try:
            import subprocess
            res = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], cwd=bot_dir, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip().lstrip("v")
        except Exception:
            pass

    # 2. Remote check via GitHub
    urls = [
        f"https://raw.githubusercontent.com/mrgluek/{bot_repo}/main/bot.py",
        f"https://git.gluek.info/gluek/{bot_repo}/raw/branch/main/bot.py",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hass-addons-version-checker"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    ver = extract_version_from_text(resp.read().decode("utf-8", errors="ignore"))
                    if ver:
                        return ver
        except Exception:
            continue

    return "N/A"

def sync_addon_version(addon_dir: str, new_ver: str) -> bool:
    addon_path = os.path.join(ADDONS_DIR, addon_dir)
    cfg_path = os.path.join(addon_path, "config.yaml")
    df_path = os.path.join(addon_path, "Dockerfile")
    ch_path = os.path.join(addon_path, "CHANGELOG.md")

    if not os.path.isfile(cfg_path):
        return False

    # 1. Update config.yaml
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg_content = f.read()
    updated_cfg = re.sub(r'version:\s*["\']?[^"\'\n]+["\']?', f'version: "{new_ver}"', cfg_content)
    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write(updated_cfg)

    # 2. Update Dockerfile
    if os.path.isfile(df_path):
        with open(df_path, "r", encoding="utf-8") as f:
            df_content = f.read()
        updated_df = re.sub(r'ARG BOT_REF=.*', f'ARG BOT_REF=v{new_ver}', df_content)
        with open(df_path, "w", encoding="utf-8") as f:
            f.write(updated_df)

    # 3. Prepend CHANGELOG.md
    if os.path.isfile(ch_path):
        with open(ch_path, "r", encoding="utf-8") as f:
            ch_content = f.read()
        if f"## {new_ver}" not in ch_content and f"## [{new_ver}]" not in ch_content:
            entry = f"## {new_ver}\n- Upstream update to version {new_ver}.\n\n"
            if ch_content.startswith("# Changelog\n"):
                parts = ch_content.split("# Changelog\n", 1)
                new_ch = "# Changelog\n\n" + entry + parts[1].lstrip()
            else:
                new_ch = entry + ch_content
            with open(ch_path, "w", encoding="utf-8") as f:
                f.write(new_ch)

    return True

def main():
    parser = argparse.ArgumentParser(description="Check or sync Delta Chat bot add-on versions.")
    parser.add_argument("--sync", action="store_true", help="Automatically bump addon versions if upstream is newer.")
    args = parser.parse_args()

    print(f"{'Add-on':<20} {'Add-on Version':<18} {'Source Version':<18} {'Status'}")
    print("-" * 68)
    
    updated = []
    for addon_dir, bot_repo in MAPPING.items():
        cfg_path = os.path.join(ADDONS_DIR, addon_dir, "config.yaml")
        addon_ver = "N/A"
        if os.path.isfile(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                addon_ver = cfg.get("version", "N/A")

        src_ver = get_source_version(bot_repo)
        
        status = "✅ Synced" if addon_ver == src_ver else "⚠️ Diff"
        if src_ver == "N/A":
            status = "ℹ️ Source not found"
        elif args.sync and addon_ver != src_ver:
            if sync_addon_version(addon_dir, src_ver):
                status = f"🔄 Synced to {src_ver}"
                updated.append((addon_dir, addon_ver, src_ver))

        print(f"{addon_dir:<20} {addon_ver:<18} {src_ver:<18} {status}")

    if updated:
        print("\nUpdated add-ons:")
        for a, old_v, new_v in updated:
            print(f"  - {a}: {old_v} -> {new_v}")
        print("\nRun: git commit -am 'Bump versions' && git push origin main")

if __name__ == "__main__":
    main()
