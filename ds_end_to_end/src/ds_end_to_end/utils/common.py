import os
import yaml
from src.ds_end_to_end import logger
import json
import joblib
from ensure import ensure_annotations
from box import ConfigBox
from pathlib import Path
from typing import Any
from box.exceptions import BoxValueError

@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content, custom_resolver=None)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e
    
@ensure_annotations
def create_directories(path_to_directories: list, verbose=False):
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:
            logger.info(f"created directory at: {path}")

@ensure_annotations
def save_json(path: Path, content: object):
    with open(path, "w") as f:
        json.dump(content, f, indent=4)

    logger.info(f"json file saved at: {path}")

@ensure_annotations
def load_json(path: Path) -> ConfigBox:
    with open(path) as f:
        content = json.load(f)

    logger.info(f"json file loaded successfully from: {path}")
    return ConfigBox(content, custom_resolver=None)


@ensure_annotations
def save_binary(file_path: Path, obj: Any):
    joblib.dump(obj, file_path)
    logger.info(f"binary file saved at: {file_path}")

@ensure_annotations
def load_binary(file_path: Path) -> Any:
    obj = joblib.load(file_path)
    logger.info(f"binary file loaded from: {file_path}")
    return obj