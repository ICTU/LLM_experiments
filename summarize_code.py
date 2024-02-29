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
from src.chat_prompt_templates import chat_code_summary_template, chat_sum_summary_template
from src.skip_dir import skip_file, skip_dir
from src.to_html import summary_to_html_enhanced


with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

class Summary(TypedDict):
    """A summary of a code file, component, application, or complete system."""

    path: str
    summary: str
    summaries: list[Summary]
    prompts: dict
    time: str
    max_tokens_chat: int
    max_tokens_summaries: int
    model_name: str
    model_chat_name: str


def summarize_files(path: Path, hash_register: HashRegister) -> Summary:
    """Summarize the files in a folder."""
    files = [subpath for subpath in path.iterdir() if subpath.is_file() and not skip_file(subpath)]
    if len(files) == 1:
        return summarize_file(files[0], hash_register)
    summaries = [summarize_file(filename, hash_register) for filename in files]
    return summarize_summaries(path, summaries, hash_register, files_only=True)


def summarize_file(filename: Path, hash_register: HashRegister) -> Summary:
    """Summarize one file."""
    with filename.open(encoding="utf-8") as code_file:
        contents = code_file.read()
    if hash_register.is_changed(str(filename), contents):
        summary_text = llm_generate_summary(path.name, contents)
        hash_register.set(str(filename), contents, summary_text)
    else:
        summary_text = hash_register.get(str(filename))
    return Summary(path=str(filename), summary=summary_text)


def summarize_summaries(
    path: Path,
    summaries: list[Summary],
    hash_register: HashRegister,
    files_only: bool = False
) -> Summary:
    """"Summarize the summaries for path."""
    key = f"files@{path}" if files_only else str(path)
    try:
        summary_texts = [summary["summary"] for summary in summaries]
        if hash_register.is_changed(key, str(summary_texts)):
            summary_text = llm_summarize_summary(path.name, summary_texts)
            hash_register.set(key, str(summary_texts), summary_text)
        else:
            summary_text = hash_register.get(key)
    except ValueError:
        print(path)
        print(summaries)
        raise
    return Summary(path=str(path), summary=summary_text, summaries=summaries)


def summarize_path(path: Path, hash_register: HashRegister) -> Summary:
    """Summarize all code in the path, recursively."""
    logging.info("Summarizing %s", path)
    dirs = [subpath for subpath in path.iterdir() if subpath.is_dir() and not skip_dir(subpath)]
    summaries = [summarize_path(subpath, hash_register) for subpath in dirs]
    summaries.append(summarize_files(path, hash_register))
    return summaries[0] if len(summaries) == 1 else summarize_summaries(path, summaries, hash_register)


def add_info_to_dict(summary, time):
    """Add configuration settings info to dictionary"""
    summary['time'] = time
    summary['max_tokens_chat'] = cfg.MAX_TOKENS_CODE
    summary['max_tokens_summaries'] = cfg.MAX_TOKENS_SUM
    summary['model_name'] = cfg.MODEL_NAME
    summary['model_chat_name'] = cfg.MODEL_CHAT_NAME
    summary['prompts'] = {
        'code_prompt':code_template,
        'summaries_prompt':summaries_template,
        'map_prompt':map_template,
        'reduce_prompt':reduce_template,
        'chat_code_prompt':str(chat_code_summary_template),
        'chat_summaries_prompt': str(chat_sum_summary_template)
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
        summaries_data = add_info_to_dict(summary, time)
        #write_json(json_data)
        #pprint.pprint(json_data, width=160)
        print(summary_to_html_enhanced(summaries_data))
    except FileNotFoundError:
        print(f"Path {sys.argv[1]} does not exist. Please provide valid path.")
    except OSError:
        print(f"Permission Denied. Please grant the necessary permissions.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
