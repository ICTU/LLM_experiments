import yaml
import box
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate

#load API key from .env
load_dotenv()

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

def llm(prompt):
    """Function for text completion LLM, takes string as input."""
    if cfg.MODEL_TYPE == "completion":
        llm = OpenAI(model=cfg.MODEL_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)
    else:
        llm = ChatOpenAI(model=cfg.MODEL_CHAT_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)
    if (nr_tokens := get_num_tokens(prompt)) > llm.max_context_size:
        raise ValueError(f"Number of tokens in prompt ({nr_tokens}) exceeds token limit ({llm.max_context_size})") 
    output = llm.invoke(prompt)
    return output


def get_num_tokens(input):
    llm = OpenAI(model=cfg.MODEL_NAME)
    num_tokens = llm.get_num_tokens(text=input)
    return num_tokens
