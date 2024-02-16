# Python script to update JSON
import json
import box
import yaml
from pathlib import Path

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

# function to add to JSON
def write_json(new_data, filename=cfg.JSON_FILE_NAME):
    if Path(filename).exists():
        with open(filename) as file:
            file_data = json.load(file)
    else:
        file_data = {}

    # Join new_data with file_data inside chosen experiment
    new_data.pop('path', None)
    file_data.setdefault(cfg.JSON_EXPERIMENT_NAME, []).append(new_data)

    with open(filename, "w") as file:
        json.dump(file_data, file, indent = 4)

