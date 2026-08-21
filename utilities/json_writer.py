import json
from pathlib import Path
from utilities.json_reader import file_path, read_file

def write_file(file_id: str, data: dict):
    path = file_path(file_id)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

def delete_file(file_id: str):
    path = file_path(file_id)
    if path.exists():
        path.unlink()

def update_file(file_id: str, field: str, value):
    data = read_file(file_id)
    data[field] = value
    write_file(file_id, data)

def write_character(guild_id: str, user_id: str, character_name: str, data: dict):
    path = character_path(guild_id, user_id, character_name)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

def delete_character(guild_id: str, user_id: str, character_name: str):
    path = character_path(guild_id, user_id, character_name)
    if path.exists():
        path.unlink()
