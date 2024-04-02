"""Write the summaries to the results file in the metrics folder."""

import json
from pathlib import Path


def write_json(new_data, filename="results.json") -> None:
    """Write the summaries to the results file."""
    if Path(filename).exists():
        with open(filename) as file:
            file_data = json.load(file)
    else:
        file_data = {}

    # Join new_data with file_data inside chosen experiment
    file_data.setdefault("experiment_1", []).append(new_data)

    with open(filename, "w") as file:
        json.dump(file_data, file, indent = 4)
