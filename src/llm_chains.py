import yaml
import box
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

#load API key from .env
load_dotenv()

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

llm = ChatOpenAI(model=cfg.MODEL_CHAT_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)

#create templates
map_template = """"The following is a set of summaries describing a parts of a codebase component. 
Summaries: {text}

Based on the list of summaries, distil a general description of the component
Helpful Answer:
"""

map_prompt = PromptTemplate(input_variables=['text'], template=map_template)

reduce_template = """The following list of summaries delineated by triple backticks describes files and directories forming a codebase component.
    List of Summaries: ```{text}```

    Take these summaries and distill them into a final consolidated summary of the component.
    Helpful answer:"""

reduce_prompt = PromptTemplate(input_variables=['text'], template=reduce_template)

#chain function
def chain_summarize_summaries(text):
    """Chain that creates chunks out of input and feeds it iteratively to an LLM"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    chunks = text_splitter.create_documents([text])
    map_reduce_chain = load_summarize_chain(
        llm=llm, 
        chain_type="map_reduce", 
        map_prompt= map_prompt, 
        combine_prompt= reduce_prompt, 
        verbose=False)
    summary = map_reduce_chain.invoke(chunks)
    return summary

