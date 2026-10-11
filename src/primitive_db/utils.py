import json
import os

from .constants import DATA_DIR


def load_metadata(filepath):
    """Load metadata from a JSON file; return {} if the file is missing."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Save metadata to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_table_data(table_name):
    """Load table rows from data/<table_name>.json; return [] if missing."""
    try:
        with open(f"{DATA_DIR}/{table_name}.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Save table rows to data/<table_name>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/{table_name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_table_data(table_name):
    """Remove the data file of a table, if any."""
    try:
        os.remove(f"{DATA_DIR}/{table_name}.json")
    except FileNotFoundError:
        pass
