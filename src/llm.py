import yaml
import box
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from pathlib import Path

from src.llm_chains import chain_summarize_summaries
from src.prompt_templates import code_summary_prompt, summaries_summary_prompt
from src.chat_prompt_templates import chat_code_summary_prompt, chat_sum_summary_prompt, one_shot_code_summary_prompt, one_shot_sum_summary_prompt
from src.tokens_weighting import max_num_tokens

#load API key from .env
load_dotenv()

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))


def llm_generate_summary(file_path: Path, code: str) -> str:
    """Generate a summary of the code, using an LLM."""
    max_tokens = max_num_tokens(file_path, cfg.BASE_MAX_TOKENS_CODE)
    if cfg.MODEL_TYPE == "completion":
        llm = create_llm(max_tokens=max_tokens)
        prompt = code_summary_prompt(file_path.name, code)
    else:
        llm = create_chat_llm(max_tokens=max_tokens)
        prompt = one_shot_code_summary_prompt(file_path.name, code)
    if is_prompt_too_big(llm, prompt):
        output = chain_summarize_summaries(code)
        return output
    else:
        output = llm.invoke(prompt)
    return output.content #use if llm is not chat: .strip()


def llm_summarize_summary(component_path: Path, summaries: list[str]) -> str:
    """Generate a summary of summaries, using an LLM."""
    max_tokens = max_num_tokens(component_path, cfg.BASE_MAX_TOKENS_SUM)
    if cfg.MODEL_TYPE == "completion":
        llm = create_llm(max_tokens=max_tokens)
        prompt = summaries_summary_prompt(component_path.name, summaries)
    else:
        llm = create_chat_llm(max_tokens=max_tokens)
        prompt = one_shot_sum_summary_prompt(component_path.name, summaries)
    if is_prompt_too_big(llm, prompt):
        output = chain_summarize_summaries(summaries)
        return output
    else:
        output = llm.invoke(prompt)
    return output.content  #use if llm is not chat: .strip()


def create_llm(max_tokens):
    """Create an completions LLM client."""
    return OpenAI(model=cfg.MODEL_NAME, temperature=cfg.TEMPERATURE, max_tokens=max_tokens)

def create_chat_llm(max_tokens):
    """Create a chat LLM client."""
    return ChatOpenAI(model=cfg.MODEL_CHAT_NAME, temperature=cfg.TEMPERATURE, max_tokens=max_tokens)

def is_prompt_too_big(llm, prompt: str) -> bool:
    """Return whether the prompt has more tokens than fit into the context."""
    return get_num_tokens(prompt) > cfg.CONTEXT_WINDOW


def get_num_tokens(input: str) -> int:
    """Return the number of tokens in prompt or output."""
    llm = OpenAI(model=cfg.MODEL_NAME)  # FIXME: Add comment explaining why we always use OpenAI to count tokens
    return llm.get_num_tokens(text=str(input))
