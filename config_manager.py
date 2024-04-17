# config_manager.py
import json  # Use json instead of ujson

def read_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)  # Changed from ujson to json
            return config
    except OSError:  # If the file does not exist, return an empty dictionary
        return {}

def write_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)  # Changed from ujson to json
