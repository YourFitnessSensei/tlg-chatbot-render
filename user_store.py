import json
import os

FILE_PATH = "user_store.json"

def load_user_map():
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_map(user_map):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(user_map, f, ensure_ascii=False, indent=2)

def add_user(username, chat_id):
    user_map = load_user_map()
    user_map[username] = chat_id
    save_user_map(user_map)
