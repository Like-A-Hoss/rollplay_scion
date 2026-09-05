import json
from pathlib import Path

DATA_DIR = Path("data/sessions")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def file_path(file_id: str) -> Path:
    return DATA_DIR / f"{file_id}.json"

def read_file(file_id: str) -> dict:
    path = file_path(file_id)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def character_path(guild_id: str, user_id: str, character_name: str) -> Path:
    folder = DATA_DIR / guild_id / user_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{character_name}.json"

def read_character(guild_id: str, user_id: str, character_name: str) -> dict:
    path = character_path(guild_id, user_id, character_name)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)
