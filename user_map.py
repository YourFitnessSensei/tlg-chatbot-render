import json
import os

USER_MAP_FILE = "user_map.json"

try:
    with open(USER_MAP_FILE, "r") as f:
        user_map = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    user_map = {}

def save_user_map():
    with open(USER_MAP_FILE, "w") as f:
        json.dump(user_map, f)
