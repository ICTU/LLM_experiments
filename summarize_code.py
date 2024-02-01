from __future__ import annotations

import logging
import pprint
import sys
from pathlib import Path
from typing import TypedDict

from langchain_openai import OpenAI


llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, max_tokens=100)


class Summary(TypedDict):
    """A summary of a code file, component, application, or complete system."""

    path: Path
    summary: str
    summaries: list[Summary]


def summarize_file(filename: Path) -> Summary:
    """Summarize one file."""
    with filename.open() as code_file:
        prompt = "Summarize the following source code file"
        summary_text = llm.invoke(f"{prompt}: ```{code_file.read()[:4000]}```")  # FIXME: deal with big files smarter
        return Summary(path=filename, summary=summary_text.strip())


def summarize_summaries(path: Path, summaries: list[Summary]) -> Summary:
    """Summarize the summaries for path."""
    prompt = "Summarize the following summaries of source code files"
    summary_text = llm.invoke(f"{prompt}: ```{str(summaries)[:4000]}```")  # FIXME: deal with lots of summaries smarter
    return Summary(path=path, summary=summary_text.strip(), summaries=summaries)


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
    dirs_to_skip = [".*", "*.egg-info", "build", "venv", "__pycache__"]
    for dir in dirs_to_skip:
        for part in path.parts:
            if part in (".", ".."):
                continue
            if Path(part).match(dir):
                return True
    return False


def skip_file(filename: Path) -> bool:
    """Return whether to skip the file."""
    filenames_to_skip = [".*", "__init__.py", "*.txt", "*.xml", "*.json"]
    for filename_to_skip in filenames_to_skip:
        if filename.match(filename_to_skip):
            return True
    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pprint.pprint(summarize_path(Path(sys.argv[1])), width=160)
