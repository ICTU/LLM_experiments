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

#get the number of tokens in prompt or output
def get_num_tokens(input):
    llm = OpenAI(model=cfg.MODEL_NAME)
    num_tokens = llm.get_num_tokens(text=input)
    return num_tokens


def llm_generate_summary(file_name, code):
    """Function for text completion LLM, takes a filename(str) and code(str) as input."""
    if cfg.MODEL_TYPE == "completion":
        llm = OpenAI(model=cfg.MODEL_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)
    else:
        llm = ChatOpenAI(model=cfg.MODEL_CHAT_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)

    #fill in prompt
    prompt = code_summary_prompt(file_name, code)
    
    #access map reduce chain if prompt is too big
    if (nr_tokens := get_num_tokens(prompt)) > llm.max_context_size:
        output = chain_summarize_summaries(code)
        #raise ValueError(f"Number of tokens in prompt ({nr_tokens}) exceeds token limit ({llm.max_context_size})") 
    
    else:
        output = llm.invoke(prompt)
    return output

def llm_summarize_summary(component, summaries):
    """Function for summarizing summaries with an LLM, takes component name (str) and summaries (list) as input"""
    if cfg.MODEL_TYPE == "completion":
        llm = OpenAI(model=cfg.MODEL_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)
    else:
        llm = ChatOpenAI(model=cfg.MODEL_CHAT_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)    

    #fill in prompt
    prompt = summaries_summary_prompt(component, summaries)

    #access map reduce chain if prompt is too big
    if (nr_tokens := get_num_tokens(prompt)) > llm.max_context_size:
        output = chain_summarize_summaries(summaries)
    else:
        output = llm.invoke(prompt)
    return output


