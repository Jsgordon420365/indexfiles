# ver #20240613054448.3

import os
import csv
import json
import time
import schedule
import threading
import pwd
import grp
import sqlite3

def initialize_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        path TEXT PRIMARY KEY,
                        size INTEGER,
                        creation_time TEXT,
                        modification_time TEXT,
                        access_time TEXT,
                        owner TEXT,
                        group TEXT,
                        permissions TEXT)''')
    conn.commit()
    conn.close()

def inventory_files(root_dir, exclude_dirs, rules=None):
    inventory = []
    for root, dirs, files in os.walk(root_dir):
        print(f"Processing directory: {root}")  # Print the current directory
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            path = os.path.join(root, file)
            if os.path.exists(path):  # Check if file exists
                size = os.path.getsize(path)
                stat = os.stat(path)
                creation_time = time.ctime(stat.st_ctime)
                modification_time = time.ctime(stat.st_mtime)
                access_time = time.ctime(stat.st_atime)
                owner = pwd.getpwuid(stat.st_uid).pw_name
                group = grp.getgrgid(stat.st_gid).gr_name
                permissions = oct(stat.st_mode)[-3:]

                file_info = {
                    "path": path,
                    "size": size,
                    "creation_time": creation_time,
                    "modification_time": modification_time,
                    "access_time": access_time,
                    "owner": owner,
                    "group": group,
                    "permissions": permissions
                }

                if rules and not apply_rules(file_info, rules):
                    continue

                inventory.append(file_info)
    return inventory

def apply_rules(file_info, rules):
    for rule in rules:
        if not eval(rule):
            return False
    return True

def write_to_csv(inventory, csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["path", "size", "creation_time", "modification_time", "access_time", "owner", "group", "permissions"])
        writer.writeheader()
        writer.writerows(inventory)

def write_to_json(inventory, json_file):
    with open(json_file, 'w') as f:
        json.dump(inventory, f, indent=4)

def update_sqlite(inventory, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    for file_info in inventory:
        cursor.execute('''INSERT OR REPLACE INTO inventory (path, size, creation_time, modification_time, access_time, owner, group, permissions)
                          VALUES (:path, :size, :creation_time, :modification_time, :access_time, :owner, :group, :permissions)''', file_info)
    
    conn.commit()
    conn.close()

def get_previous_inventory(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inventory')
    rows = cursor.fetchall()
    previous_inventory = {row[0]: row[1:] for row in rows}
    conn.close()
    return previous_inventory

def detect_changes(current_inventory, previous_inventory):
    changes = []
    current_paths = {file_info['path'] for file_info in current_inventory}
    previous_paths = set(previous_inventory.keys())

    added_or_modified = current_paths - previous_paths
    removed = previous_paths - current_paths

    for file_info in current_inventory:
        if file_info['path'] in added_or_modified or file_info != previous_inventory.get(file_info['path']):
            changes.append(file_info)
    
    for path in removed:
        changes.append({"path": path, "action": "deleted"})
    
    return changes

def job():
    root_dir = "/Users/gordo"
    exclude_dirs = [
        "node_modules",
        "another_folder_to_exclude"
    ]
    rules = [
        'file_info["size"] > 1024',  # Example rule: only include files larger than 1KB
        'file_info["owner"] == "gordo"'  # Example rule: only include files owned by "gordo"
    ]
    
    current_inventory = inventory_files(root_dir, exclude_dirs, rules)
    previous_inventory = get_previous_inventory("inventory.db")
    changes = detect_changes(current_inventory, previous_inventory)

    write_to_csv(changes, "inventory_changes.csv")
    write_to_json(changes, "inventory_changes.json")
    update_sqlite(current_inventory, "inventory.db")

def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

initialize_db("inventory.db")
schedule.every().hour.do(job)
stop_run_continuously = run_continuously()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_run_continuously.set()

# Version History:
# 20240613054448.1 - Initial version.
# 20240613054448.2 - Added periodic execution, advanced metadata extraction, rule-based system.
# 20240613054448.3 - Enhanced with SQLite integration, incremental updates, change detection, and logging.

# This script now includes:
# - Periodic execution using the 'schedule' library.
# - Advanced metadata extraction (access time, owner, group, permissions).
# - A rule-based system to include/exclude files based on specific criteria.
# - Storage of inventory data in an SQLite database.
# - Incremental updates by comparing current and previous inventory data.
# - Detection of changes to only process and store differences.
# Remember to install the 'schedule' library if not already installed: pip install schedule
