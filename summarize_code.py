from __future__ import annotations
import logging
import pprint
import sys
import timeit
import yaml
import box
from pathlib import Path
from typing import TypedDict

from src.add_to_JSON import write_json
from src.hash_register import load_hashes, save_hashes, HashRegister
from src.llm import llm_generate_summary, llm_summarize_summary
from src.prompt_templates import code_template, summaries_template, map_template, reduce_template


with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

class Summary(TypedDict):
    """A summary of a code file, component, application, or complete system."""

    path: Path
    path_str: str ###added because unable to save raw path to json file
    summary: str
    summaries: list[Summary]
    prompts: dict
    time: str
    max_tokens: int
    model_name: str
    model_chat_name: str


def summarize_file(filename: Path, hash_register: HashRegister) -> Summary:
    """Summarize one file."""
    with filename.open(encoding="utf-8") as code_file:
        contents = code_file.read()
        if hash_register.is_changed(str(filename), contents):
            summary_text = llm_generate_summary(path.name, contents)
            hash_register.set(str(filename), contents, summary_text)
        else:
            summary_text = hash_register.get(str(filename))
        print(summary_text)
        return Summary(path_str=str(filename), summary=summary_text)


def summarize_summaries(path: Path, summaries: list[Summary], hash_register: HashRegister) -> Summary:
    """"Summarize the summaries for path."""
    try:
        summary_texts = [summary["summary"] for summary in summaries]
        if hash_register.is_changed(str(path), str(summary_texts)):
            summary_text = llm_summarize_summary(path.name, summary_texts)
            hash_register.set(str(path), str(summary_texts), summary_text)
        else:
            summary_text = hash_register.get(str(path))
        print(summary_text)
    except ValueError:
        print(path)
        print(summaries)
        raise
    return Summary(path=path, path_str=str(path), summary=summary_text, summaries=summaries)


def summarize_path(path: Path, hash_register: HashRegister) -> Summary:
    """Summarize all code in the path, recursively."""
    summaries = []
    for subpath in path.iterdir():
        if (subpath.is_dir() and skip_dir(subpath)) or skip_file(subpath):
            continue
        logging.info("Summarizing %s", subpath)
        summary_dict = summarize_path(subpath, hash_register) if subpath.is_dir() else summarize_file(subpath, hash_register)
        summary_dict.pop('path', None) ### remove path to be able to save as json
        summaries.append(summary_dict)
    return summarize_summaries(path, summaries, hash_register)


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
    filenames_to_skip = [".*", "__init__.py", "*.txt", "*.xml", "*.json", "*.png", "*.ico", "*.gif"]
    for filename_to_skip in filenames_to_skip:
        if filename.match(filename_to_skip):
            return True
    return False


def add_info_to_dict(summary, time):
    """Add configuration settings info to dictionary"""
    summary['time'] = time
    summary['max_tokens'] = cfg.MAX_TOKENS
    summary['model_name'] = cfg.MODEL_NAME
    summary['model_chat_name'] = cfg.MODEL_CHAT_NAME
    summary['prompts'] = {
        'code_prompt':code_template,
        'summaries_prompt':summaries_template,
        'map_prompt':map_template,
        'reduce_prompt':reduce_template
        }
    return summary


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        path = Path(sys.argv[1]).resolve(strict=True)
        start = timeit.default_timer()
        summary_cache = Path(".summary_cache.json")
        hash_register = load_hashes(summary_cache)
        summary = summarize_path(path, hash_register)
        save_hashes(summary_cache, hash_register)
        end = timeit.default_timer()
        time =  f"{round((end-start)/60)} minutes" if (end-start) > 100 else f"{round(end-start)} seconds"
        json_data = add_info_to_dict(summary, time)
        write_json(json_data)
        pprint.pprint(json_data, width=160)
    except FileNotFoundError:
        print(f"Path {sys.argv[1]} does not exist. Please provide valid path.")
    except OSError:
        print(f"Permission Denied. Please grant the necessary permissions.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")