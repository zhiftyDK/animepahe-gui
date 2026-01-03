import os
import sys
import shutil
import subprocess
import requests

def github_updater(repo: str, current_version: str):
    """
    Checks GitHub for a newer release than current_version.
    If a newer release exists, downloads the first asset and replaces
    the running script with the new version, then restarts itself.
    
    :param repo: GitHub repository in the form "username/repo"
    :param current_version: Current version of your script, e.g., "v1.0.0"
    """
    SCRIPT_PATH = os.path.realpath(__file__)
    TMP_PATH = SCRIPT_PATH + ".tmp"

    # ---------------- 1. Fetch latest release ----------------
    try:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        r = requests.get(url)
        r.raise_for_status()
        release = r.json()
        latest_version = release["tag_name"]
        assets = release.get("assets", [])
    except Exception as e:
        print(f"[Updater] Failed to fetch latest release: {e}")
        return  # Do nothing if we can't fetch release

    # ---------------- 2. Compare versions ----------------
    if latest_version == current_version:
        print(f"[Updater] You are already on the latest version: {current_version}")
        return
    print(f"[Updater] New version available: {latest_version}")

    # ---------------- 3. Download the first asset ----------------
    if not assets:
        print("[Updater] No assets found in the release, cannot update.")
        return

    asset_url = assets[0]["browser_download_url"]
    print(f"[Updater] Downloading new version from {asset_url}...")
    try:
        r = requests.get(asset_url, stream=True, verify=False)
        r.raise_for_status()
        with open(TMP_PATH, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    except Exception as e:
        print(f"[Updater] Failed to download update: {e}")
        return

    print(f"[Updater] Downloaded to temporary file: {TMP_PATH}")

    # ---------------- 4. Replace old script and restart ----------------
    print("[Updater] Updating script and restarting...")
    try:
        subprocess.Popen([
            sys.executable, "-c",
            f"import shutil, os, time, sys; "
            f"time.sleep(1); "
            f"shutil.move(r'{TMP_PATH}', r'{SCRIPT_PATH}'); "
            f"os.execv(r'{sys.executable}', [r'{sys.executable}', r'{SCRIPT_PATH}'])"
        ])
        sys.exit(0)  # Exit old script safely
    except Exception as e:
        print(f"[Updater] Failed to restart script: {e}")
        return