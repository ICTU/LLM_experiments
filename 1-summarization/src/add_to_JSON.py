"""Write the summaries to the results file in the metrics folder."""

import json
from pathlib import Path

import box
import yaml

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))


def write_json(new_data, filename=cfg.JSON_FILE_NAME) -> None:
    """Write the summaries to the results file."""
    if Path(filename).exists():
        with open(filename) as file:
            file_data = json.load(file)
    else:
        file_data = {}

    # Join new_data with file_data inside chosen experiment
    file_data.setdefault(cfg.JSON_EXPERIMENT_NAME, []).append(new_data)

    with open(filename, "w") as file:
        json.dump(file_data, file, indent = 4)
