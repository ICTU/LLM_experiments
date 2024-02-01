import yaml
import box
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from src.add_to_JSON import write_json
#from langchain_community.document_loaders import WebBaseLoader

#load API key from .env
load_dotenv()

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

#initalize OpenAI model
llm = OpenAI(model=cfg.MODEL_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)

#prompt template for code summary
template = """"
Write a concise summary for the code delineated by the triple backticks. 

Code: ```{code}```
"""
prompt = PromptTemplate(input_variables=["code"], template=template)

#link to all python files in a directory
directory_in_str = cfg.DIRECTORY_PATH

pathlist = Path(directory_in_str).glob('**/*.py')

component = Path(cfg.DIRECTORY_PATH).name

#read code as string
def read_code_as_str(code_filepath):
    code_str = code_filepath.read_text()
    return code_str

#loop through files in directory
for path in pathlist:
    #check for empty files
    code_str = read_code_as_str(path)
    
    if code_str == "":
        continue

    #place code from path into the prompt
    summary_prompt = prompt.format(code=code_str)

    #keep track of tokens used for prompt
    num_tokens_prompt = llm.get_num_tokens(summary_prompt)

    print(f"This prompt, including code, contains {num_tokens_prompt} tokens")
    print("\n")

    if num_tokens_prompt > cfg.CONTEXT_WINDOW: 
        #if number of tokens exceeds context window of model, use "stuff" summarization
        chain = load_summarize_chain(llm, chain_type="stuff")
        summary = chain.invoke(code_str)

    else:            
        #else generate summary using prompt
        summary = llm.invoke(summary_prompt)
    
    print(f"File: {path} \n Summary: \n {summary}")
    print("\n")

    num_tokens_output = llm.get_num_tokens(summary)

    #add summary to JSON
    json_item = {
                "name": path.name,
                "path": f"({path})",
                "summary": summary,
                "prompt_template": template,               
                "max_tokens": cfg.MAX_TOKENS,
                "num_tokens_prompt": num_tokens_prompt,
                "num_tokens_output": num_tokens_output,
                "model": cfg.MODEL_NAME,
                "component": component
                 }
    write_json(json_item)



# code for "stuff" type summarization with scraper

# loader = WebBaseLoader("https://raw.githubusercontent.com/ICTU/quality-time/master/components/notifier/src/notifier/notifier.py")
# docs = loader.load()

# llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106")
# chain = load_summarize_chain(llm, chain_type="stuff")

# print(chain.invoke(docs))