import yaml
import box
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI

from src.llm_chains import chain_summarize_summaries
from src.prompt_templates import code_summary_prompt, summaries_summary_prompt

#load API key from .env
load_dotenv()

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))


def llm_generate_summary(file_name: str, code: str) -> str:
    """Generate a summary of the code, using an LLM."""
    llm = create_llm()
    prompt = code_summary_prompt(file_name, code)
    if is_prompt_too_big(llm, prompt):
        output = chain_summarize_summaries(code)  # FIXME: What is the prompt used here?
    else:
        output = llm.invoke(prompt)
    return output.strip()


def llm_summarize_summary(component: str, summaries: list[str]) -> str:
    """Generate a summary of summaries, using an LLM."""
    llm = create_llm()
    prompt = summaries_summary_prompt(component, summaries)
    if is_prompt_too_big(llm, prompt):
        output = chain_summarize_summaries(summaries)  # FIXME: What is the prompt used here?
    else:
        output = llm.invoke(prompt)
    return output.strip()


def create_llm() -> OpenAI | ChatOpenAI:
    """Create an LLM client to use based on the configuration."""
    llm_class = OpenAI if cfg.MODEL_TYPE == "completion" else ChatOpenAI
    return llm_class(model=cfg.MODEL_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)


def is_prompt_too_big(llm, prompt: str) -> bool:
    """Return whether the prompt has more tokens than fit into the context."""
    return get_num_tokens(prompt) > llm.max_context_size


def get_num_tokens(input: str) -> int:
    """Return the number of tokens in prompt or output."""
    llm = OpenAI(model=cfg.MODEL_NAME)  # FIXME: Add comment explaining why we always use OpenAI to count tokens
    return llm.get_num_tokens(text=input)
