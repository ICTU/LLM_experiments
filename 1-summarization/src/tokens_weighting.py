import os
import math
from pathlib import Path

from src.skip_dir import skip_dir, skip_file


def number_of_files(dir_path:Path) -> int:
    """Count number of files in a directory"""
    count = 0
    for path in os.scandir(dir_path):
        if path.is_file() and not skip_file(Path(path)):
            count += 1
        if path.is_dir() and not skip_dir(Path(path)):
            count += number_of_files(path)

        else: continue
    return count


def max_num_tokens(path: Path, base_max_tokens) -> int:
    """Calculate the max numer of tokens usable in the output, takes base tokens and number of files as int input"""
    number_of_files_in_dir = number_of_files(path)
    max_num_tokens = math.ceil(base_max_tokens + math.sqrt(number_of_files_in_dir * 30))
    return max_num_tokens