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
    print(summary_text)
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
        print(summary_text)
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
    return summarize_summaries(path, summaries, hash_register)


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



def summary_to_markdown(summary: Summary, level: int = 1, is_nested: bool = False) -> str:
    """
    Converts a Summary instance to a markdown formatted string, improving structure and readability.
    Now supports a more tree-like structure for nested summaries with collapsible sections.
    
    :param summary: The Summary instance to convert.
    :param level: The current heading level for markdown formatting.
    :param is_nested: Indicates if the current summary is a nested summary.
    :return: A markdown formatted string.
    """
    markdown_lines = []
    
    # Heading for the summary
    path = summary.get('path', 'Unknown Path')
    if is_nested:
        markdown_lines.append(f"<details><summary>{'#' * level} Path: {path}</summary>\n\n")
    else:
        markdown_lines.append(f"{'#' * level} Path: {path}\n")
    
    # Summary description
    summary_text = summary.get('summary', 'No summary provided.')
    markdown_lines.append(f"*Summary:* {summary_text}\n")
    
    if not is_nested:
        # Details are only included for the primary layer
        markdown_lines.append(f"\n{'#' * (level + 1)} Configuration Details:\n")
        time = summary.get('time', 'Unknown Time')
        max_tokens_chat = summary.get('max_tokens_chat', 'N/A')
        max_tokens_summaries = summary.get('max_tokens_summaries', 'N/A')
        model_name = summary.get('model_name', 'Unknown Model')
        model_chat_name = summary.get('model_chat_name', 'Unknown Chat Model')
        
        markdown_lines.append(f"- **Time Generated:** {time}\n")
        markdown_lines.append(f"- **Max Tokens for Chat:** {max_tokens_chat}\n")
        markdown_lines.append(f"- **Max Tokens for Generating Summaries:** {max_tokens_summaries}\n")
        markdown_lines.append(f"- **Model Used for Summaries:** {model_name}\n")
        markdown_lines.append(f"- **Model Used for Chat:** {model_chat_name}\n")
        
        # Prompts are also only included for the primary layer
        prompts = summary.get('prompts', {})
        if prompts:
            markdown_lines.append(f"\n{'#' * (level + 2)} Used Prompts:\n")
            for name, prompt in prompts.items():
                markdown_lines.append(f"- **Prompt:** {name}\n  - {prompt}\n")
    
    # Input Summaries
    summaries = summary.get('summaries', [])
    if summaries:
        markdown_lines.append(f"\n{'#' * (level)} Summaries used as input:\n")
        for nested_summary in summaries:
            markdown_lines.append(summary_to_markdown(nested_summary, level + 1, is_nested=True))
    
    if is_nested:
        markdown_lines.append("\n</details>")  # Close the details tag for nested summaries
    
    return '\n'.join(markdown_lines)



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
        #write_json(json_data)
        #pprint.pprint(json_data, width=160)
        print(summary_to_markdown(json_data))
    except FileNotFoundError:
        print(f"Path {sys.argv[1]} does not exist. Please provide valid path.")
    # except OSError:
    #     print(f"Permission Denied. Please grant the necessary permissions.")
    # except Exception as e:
    #     print(f"Unexpected error occurred: {e}")