from pathlib import Path

def skip_dir(path: Path) -> bool:
    """Return whether to skip the directory."""
    dirs_to_skip = [".*", "*.egg-info", "build", "venv", "__pycache__", "testdata"]
    for dir in dirs_to_skip:
        for part in path.parts:
            if part in (".", ".."):
                continue
            if Path(part).match(dir):
                return True
    return False


def skip_file(filename: Path) -> bool:
    """Return whether to skip the file."""
    filenames_to_skip = [".*", "__init__.py", "*.txt", "*.xml", "*.json", "*.png", "*.ico", "*.gif", "*.zip", "summarize_code.py", "...summary_cache.json", "*.pdf", "*.docx"]
    for filename_to_skip in filenames_to_skip:
        if filename.match(filename_to_skip):
            return True
    return False

