import yaml
import box
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.prompt_templates import map_prompt, reduce_prompt

#load API key from .env
load_dotenv()

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

llm = ChatOpenAI(model=cfg.MODEL_CHAT_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS_CHAIN)

#chain function
def chain_summarize_summaries(text):
    """Chain that creates chunks out of input and feeds it iteratively to an LLM"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=cfg.CHUNK_SIZE, chunk_overlap=0)
    chunks = text_splitter.create_documents([text])
    map_reduce_chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt= map_prompt,
        combine_prompt= reduce_prompt,
        verbose=False)
    summary = map_reduce_chain.invoke(chunks)
    return summary["output_text"]
