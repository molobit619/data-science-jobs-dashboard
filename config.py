import os
import json


def get_config():
    key_dict = {}
    keys_json_path = os.path.expanduser(os.path.join(".", ".api_keys.json"))
    if os.path.exists(keys_json_path):
        with open(keys_json_path, 'r') as keys_file:
            key_dict = json.load(keys_file)
    else:
        print(f"Could not find {keys_json_path}")

    return key_dict
