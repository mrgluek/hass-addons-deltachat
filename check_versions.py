#!/usr/bin/env python3
"""Helper script to check and sync bot versions in sibling repositories against addon configs."""

import argparse
import os
import re
import subprocess
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

# Files that may hold the VERSION constant (some bots moved it out of bot.py)
VERSION_FILES = ["bot.py", "config.py", "dc_commands.py", "commands.py"]

def highest_version_tag(ls_remote_output: str) -> str:
    versions = re.findall(r"refs/tags/v(\d+(?:\.\d+)*)$", ls_remote_output, re.M)
    return max(versions, key=lambda v: tuple(int(p) for p in v.split(".")), default="")

def get_latest_tag_version(bot_repo: str) -> str:
    # The add-on Dockerfile clones BOT_REF=v<version>, so the newest pushed tag is
    # the version that can actually be built (and no CDN cache is involved).
    for url in (f"https://github.com/mrgluek/{bot_repo}.git", f"https://git.gluek.info/gluek/{bot_repo}.git"):
        try:
            res = subprocess.run(["git", "ls-remote", "--tags", "--refs", url], capture_output=True, text=True,
                                 timeout=20, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
        except Exception:
            continue
        if res.returncode == 0:
            ver = highest_version_tag(res.stdout)
            if ver:
                return ver
    return ""

def get_source_version(bot_repo: str) -> str:
    # 1. Newest version tag on GitHub / Forgejo
    ver = get_latest_tag_version(bot_repo)
    if ver:
        return ver

    # 2. Local filesystem check
    bot_dir = os.path.join(PARENT_DIR, bot_repo)
    if os.path.isdir(bot_dir):
        for name in VERSION_FILES:
            path = os.path.join(bot_dir, name)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    ver = extract_version_from_text(f.read())
                    if ver:
                        return ver
        try:
            res = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], cwd=bot_dir, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip().lstrip("v")
        except Exception:
            pass

    # 3. Remote file check via GitHub / Forgejo (supports main and master branches)
    branches = ["main", "master"]
    urls = []
    for branch in branches:
        for name in VERSION_FILES:
            urls.append(f"https://raw.githubusercontent.com/mrgluek/{bot_repo}/{branch}/{name}")
            urls.append(f"https://git.gluek.info/gluek/{bot_repo}/raw/branch/{branch}/{name}")

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

def get_upstream_changelog(bot_repo: str) -> str:
    # 1. Local filesystem check
    bot_dir = os.path.join(PARENT_DIR, bot_repo)
    if os.path.isdir(bot_dir):
        ch_file = os.path.join(bot_dir, "CHANGELOG.md")
        if os.path.isfile(ch_file):
            try:
                with open(ch_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass

    # 2. Remote check via GitHub / Forgejo
    branches = ["main", "master"]
    urls = []
    for branch in branches:
        urls.append(f"https://raw.githubusercontent.com/mrgluek/{bot_repo}/{branch}/CHANGELOG.md")
        urls.append(f"https://git.gluek.info/gluek/{bot_repo}/raw/branch/{branch}/CHANGELOG.md")

    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hass-addons-version-checker"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return resp.read().decode("utf-8", errors="ignore")
        except Exception:
            continue

    return ""

def parse_version(version: str):
    """Return the version as a tuple of ints for comparison, or None if it is not numeric."""
    try:
        return tuple(int(p) for p in str(version).strip().split("."))
    except ValueError:
        return None

# A release heading in a bot changelog: "## 1.2.3" or "## [1.2.3] - 2026-10-16"
VERSION_HEADER_RE = re.compile(r'^##\s*\[?(\d+(?:\.\d+)*)\]?(?:\s*-.*)?\s*$')

def extract_changelog_sections(changelog_text: str, old_version: str, new_version: str) -> list:
    """Return [(version, notes)] for every upstream section with old_version < version <= new_version,
    newest first. If old_version is not a usable version, only new_version's section is returned."""
    new_t = parse_version(new_version)
    old_t = parse_version(old_version)
    if not changelog_text or new_t is None:
        return []

    sections = {}
    current = None
    for line in changelog_text.splitlines():
        m = VERSION_HEADER_RE.match(line)
        if m:
            current = m.group(1)
            sections.setdefault(current, [])
        elif re.match(r'^##\s+', line):
            current = None  # e.g. "## [Unreleased]": not a release, skip its body
        elif current is not None:
            sections[current].append(line)

    result = []
    for ver, body in sections.items():
        t = parse_version(ver)
        if t is None or t > new_t:
            continue
        if old_t is not None and t <= old_t:
            continue
        if old_t is None and t != new_t:
            continue
        result.append((ver, "\n".join(body).strip()))
    result.sort(key=lambda item: parse_version(item[0]), reverse=True)
    return result

def has_changelog_entry(ch_content: str, version: str) -> bool:
    # Anchored match so "## 2.1" is not mistaken for "## 2.12"
    return re.search(rf'^##\s*\[?{re.escape(version)}\]?(?:\s|$)', ch_content, re.M) is not None

def sync_addon_version(addon_dir: str, new_ver: str, bot_repo: str = "", addons_dir: str = None) -> bool:
    addon_path = os.path.join(addons_dir or ADDONS_DIR, addon_dir)
    cfg_path = os.path.join(addon_path, "config.yaml")
    df_path = os.path.join(addon_path, "Dockerfile")
    ch_path = os.path.join(addon_path, "CHANGELOG.md")

    if not os.path.isfile(cfg_path):
        return False

    # 1. Update config.yaml (remember the old version to know which changelog sections are new)
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg_content = f.read()
    old_ver = str((yaml.safe_load(cfg_content) or {}).get("version", ""))
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

    # 3. Prepend CHANGELOG.md with every upstream section newer than the old add-on version,
    #    so intermediate releases are not lost when the bot jumps several versions at once
    if os.path.isfile(ch_path):
        with open(ch_path, "r", encoding="utf-8") as f:
            ch_content = f.read()
        if not has_changelog_entry(ch_content, new_ver):
            upstream_text = get_upstream_changelog(bot_repo) if bot_repo else ""
            sections = extract_changelog_sections(upstream_text, old_ver, new_ver)
            if new_ver not in (ver for ver, _ in sections):
                sections.insert(0, (new_ver, ""))
            entries = []
            for ver, notes in sections:
                if has_changelog_entry(ch_content, ver):
                    continue
                if notes:
                    entries.append(f"## {ver}\n\n{notes}\n\n")
                else:
                    entries.append(f"## {ver}\n- Upstream update to version {ver}.\n\n")
            entry = "".join(entries)

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
            if sync_addon_version(addon_dir, src_ver, bot_repo):
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
