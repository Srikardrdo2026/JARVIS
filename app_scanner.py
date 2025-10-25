import os
import csv
import subprocess
import json
import glob
import win32com.client

CSV_FILE = "installed_apps.csv"

START_MENU_DIRS = [
    os.path.join(os.environ["PROGRAMDATA"], r"Microsoft\Windows\Start Menu\Programs"),
    os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
]

PROGRAM_FILES_DIRS = [
    os.environ.get("ProgramFiles", r"C:\Program Files"),
    os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
]

def process_shortcut(file, root, shell):
    if not file.lower().endswith(".lnk"):
        return None
    try:
        shortcut_path = os.path.join(root, file)
        shortcut = shell.CreateShortCut(shortcut_path)
        target = shortcut.Targetpath
        name = os.path.splitext(file)[0]
        return (name, target, shortcut_path, "")
    except Exception as e:
        print(f"[ERROR] Failed to read shortcut {file}: {e}")
        return None

def scan_shortcuts():
    print("[DEBUG] Scanning Start Menu shortcuts...")
    apps = []
    shell = win32com.client.Dispatch("WScript.Shell")
    for directory in START_MENU_DIRS:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    result = process_shortcut(file, root, shell)
                    if result:
                        apps.append(result)
    return apps

def process_executable(file, root):
    if not file.lower().endswith(".exe"):
        return None
    path = os.path.join(root, file)
    name = os.path.splitext(file)[0]
    return (name, path, "", "")

def scan_program_files():
    print("[DEBUG] Scanning Program Files...")
    apps = []
    for directory in PROGRAM_FILES_DIRS:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    result = process_executable(file, root)
                    if result:
                        apps.append(result)
    return apps

def scan_uwp_apps():
    print("[DEBUG] Scanning UWP apps...")
    try:
        result = subprocess.run(["powershell", "-Command", "Get-StartApps | ConvertTo-Json"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] PowerShell error: {result.stderr}")
            return []
        uwp_data = json.loads(result.stdout)
        if isinstance(uwp_data, dict):
            uwp_data = [uwp_data]
        apps = [(app["Name"], "", "", app["AppID"]) for app in uwp_data if "Name" in app and "AppID" in app]
        return apps
    except Exception as e:
        print(f"[ERROR] Failed to get UWP apps: {e}")
        return []

def scan_discord():
    """Scan and return actual Discord.exe path if found."""
    local_appdata = os.environ.get("LOCALAPPDATA")
    discord_base = os.path.join(local_appdata, "Discord")
    if not os.path.exists(discord_base):
        return []

    try:
        subdirs = sorted(glob.glob(os.path.join(discord_base, "app-*")), reverse=True)
        for subdir in subdirs:
            discord_exe = os.path.join(subdir, "Discord.exe")
            if os.path.exists(discord_exe):
                print(f"[DEBUG] Found actual Discord executable: {discord_exe}")
                return [("Discord", discord_exe, "", "")]
    except Exception as e:
        print(f"[ERROR] Failed to scan Discord path: {e}")
    return []

def deduplicate_apps(apps):
    seen_names = set()
    unique_apps = []
    for app in apps:
        if app[0] not in seen_names:
            unique_apps.append(app)
            seen_names.add(app[0])
    return unique_apps

def write_to_csv(apps):
    print("[DEBUG] Writing to CSV...")
    try:
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["AppName", "ExecutablePath", "ShortcutPath", "AppUserModelID"])
            for app in apps:
                writer.writerow(app)
        print(f"[DEBUG] Successfully wrote {len(apps)} apps to {CSV_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to write to {CSV_FILE}: {e}")

def scan_and_save():
    shortcuts = scan_shortcuts()
    executables = scan_program_files()
    uwp_apps = scan_uwp_apps()
    discord_app = scan_discord()

    all_apps = shortcuts + executables + uwp_apps + discord_app
    unique_apps = deduplicate_apps(all_apps)
    write_to_csv(unique_apps)
    print(f"Scan complete. {len(unique_apps)} unique apps saved to {CSV_FILE}")

if __name__ == "__main__":
    scan_and_save()
