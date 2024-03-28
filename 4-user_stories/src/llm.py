from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


#load API key from .env
load_dotenv()

model = "gpt-4-0125-preview"
context_window = 16385

def create_llm(max_tokens=None):
    """initiates an OpenAI chat completions llm"""
    return ChatOpenAI(model=model, temperature=0.1, max_tokens=max_tokens)

def get_num_tokens(prompt) -> int:
    """Return the number of tokens in prompt or output."""
    llm = ChatOpenAI(model=model)
    return llm.get_num_tokens_from_messages(prompt)

def is_prompt_too_big(llm, prompt: str) -> bool:
    """Return whether the prompt has more tokens than fit into the context."""
    return get_num_tokens(prompt) > context_window