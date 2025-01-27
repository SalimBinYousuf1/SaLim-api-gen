import os
from typing import List, Dict, Any
import yaml
import json


def ensure_directory(file_path: str) -> None:
    """
    Ensure that the directory for the given file path exists.
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def list_openapi_files(directory: str) -> List[str]:
    """
    List all OpenAPI specification files (JSON or YAML) in the given directory.
    """
    openapi_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".json", ".yaml", ".yml")):
                openapi_files.append(os.path.join(root, file))
    return openapi_files


def load_yaml(file_path: str) -> Dict[str, Any]:
    """
    Load a YAML file and return its contents as a dictionary.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file and return its contents as a dictionary.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def save_yaml(data: Dict[str, Any], file_path: str) -> None:
    """
    Save a dictionary as a YAML file.
    """
    with open(file_path, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """
    Save a dictionary as a JSON file.
    """
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.
    """
    for key, value in dict2.items():
        if isinstance(value, dict):
            dict1[key] = merge_dicts(dict1.get(key, {}), value)
        else:
            dict1[key] = value
    return dict1
