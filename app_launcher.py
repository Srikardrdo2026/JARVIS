import os
import subprocess
import csv
import psutil
from difflib import get_close_matches
from speech import say

CSV_FILE = "installed_apps.csv"

def load_installed_apps():
    if not os.path.exists(CSV_FILE):
        print(f"[WARN] {CSV_FILE} not found. Please run the app scanner first.")
        return []

    apps = []
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            apps.append((
                row["AppName"].lower(),
                row.get("ExecutablePath", ""),
                row.get("ShortcutPath", ""),
                row.get("AppUserModelID", "")
            ))
    return apps

def find_app_path(app_name, apps):
    app_name = app_name.lower()
    all_app_names = [name for name, _, _, _ in apps]

    for name, exe_path, shortcut_path, app_user_model_id in apps:
        if app_name in name:
            return exe_path or shortcut_path, app_user_model_id

    close_matches = get_close_matches(app_name, all_app_names, n=1, cutoff=0.6)
    if close_matches:
        matched_name = close_matches[0]
        for name, exe_path, shortcut_path, app_user_model_id in apps:
            if name == matched_name:
                return exe_path or shortcut_path, app_user_model_id

    return None, None

def open_app(query):
    app_name = query.lower().replace("open", "").strip()

    apps = load_installed_apps()
    if not apps:
        say("I don't have the list of installed applications. Please update the app list first.")
        return False

    app_path, app_user_model_id = find_app_path(app_name, apps)

    if app_user_model_id:
        try:
            print(f"[DEBUG] Launching UWP app with AppUserModelID: {app_user_model_id}")
            subprocess.Popen(['explorer.exe', f'shell:AppsFolder\\{app_user_model_id}'])
            say(f"Launching {app_name}.")
            return True
        except Exception as e:
            print(f"[ERROR] Could not launch UWP app {app_user_model_id}: {e}")
            say(f"Sorry, I couldn't launch {app_name}.")
            return False

    elif app_path:
        try:
            print(f"[DEBUG] Launching traditional app at path: {app_path}")
            os.startfile(app_path)
            say(f"Launching {app_name}.")
            return True
        except Exception as e:
            print(f"[ERROR] Could not open {app_path}: {e}")
            say(f"Sorry, I encountered an error while opening {app_name}.")
            return False
    else:
        print(f"[DEBUG] App not found: {app_name}")
        say(f"I couldn't find {app_name} on your system.")
        return False

def close_app(query):
    app_name = query.lower().replace("close", "").strip()
    matched_processes = []

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name'].lower()
            if app_name in pname:
                matched_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not matched_processes:
        say(f"I couldn't find any running app named {app_name}.")
        return False

    for proc in matched_processes:
        try:
            print(f"[DEBUG] Terminating process: {proc.name()} (PID: {proc.pid})")
            proc.terminate()
        except Exception as e:
            print(f"[ERROR] Failed to terminate {proc.name()}: {e}")

    say(f"Closed {app_name}.")
    return True
