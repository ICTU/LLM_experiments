from __future__ import annotations
import logging
import pprint
import sys
from pathlib import Path
from typing import TypedDict
from src.llm import llm_generate_summary, llm_summarize_summary
from src.prompt_template import code_template, summaries_template


class Summary(TypedDict):
    """A summary of a code file, component, application, or complete system."""

    path: Path
    summary: str
    prompt: str
    summaries: list[Summary]


def summarize_file(filename: Path) -> Summary:
    """Summarize one file."""
    with filename.open() as code_file:
        #add code and file_name to prompt
        summary_text = llm_generate_summary(path.name, code_file.read())
        print(summary_text)
        return Summary(path=filename, prompt=code_template, summary=summary_text.strip())


def summarize_summaries(path: Path, summaries: list[Summary]) -> Summary:
    """"Summarize the summaries for path."""
    try:
        summary_text = llm_summarize_summary(path.name, [summary["summary"] for summary in summaries])
        print(summary_text)
    except ValueError:
        print(path)
        print(summaries)
        raise
    return Summary(path=path, prompt=summaries_template, summary=summary_text.strip(), summaries=summaries)


def summarize_path(path: Path) -> Summary:
    """Summarize all code in the path, recursively."""
    summaries = []
    for subpath in path.iterdir():
        if (subpath.is_dir() and skip_dir(subpath)) or skip_file(subpath):
            continue
        logging.info("Summarizing %s", subpath)
        summaries.append(summarize_path(subpath) if subpath.is_dir() else summarize_file(subpath))
    return summarize_summaries(path, summaries)


def skip_dir(path: Path) -> bool:
    """Return whether to skip the directory."""
    dirs_to_skip = ["*.egg-info", "build", "venv", "__pycache__"]
    for dir in dirs_to_skip:
        for part in path.parts:
            if part in (".", ".."):
                continue
            if Path(part).match(dir):
                return True
    return False


def skip_file(filename: Path) -> bool:
    """Return whether to skip the file."""
    filenames_to_skip = ["__init__.py", "*.txt", "*.xml", "*.json"]
    for filename_to_skip in filenames_to_skip:
        if filename.match(filename_to_skip):
            return True
    return False


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        path = Path(sys.argv[1]).resolve(strict=True)
        summary = summarize_path(path)
        pprint.pprint(summary, width=160)
    except FileNotFoundError:
        print(f"Path {sys.argv[1]} does not exist. Please provide valid path.")
    except OSError:
        print(f"Permission Denied. Please grant the necessary permissions.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")