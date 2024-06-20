from pathlib import Path

def skip_dir(path: Path) -> bool:
    """Return whether to skip the directory."""
    dirs_to_skip = [".*", "*.egg-info", "build", "venv", "__pycache__", "testdata", "metrics", "docs", "example_files"]

    return any(path.match(dir_pattern) for dir_pattern in dirs_to_skip)


def skip_file(file_path: Path) -> bool:
    """Return whether to skip the file."""
    filenames_to_skip = [".*", "__init__.py", "*.txt", "*.xml", "*.json", "*.png", "*.ico", "*.gif", "*.zip", "summarize_code.py", "...summary_cache.json", "*.pdf", "*.docx"]
    return any(file_path.match(file_pattern) for file_pattern in filenames_to_skip)

