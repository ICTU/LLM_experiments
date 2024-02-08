import yaml
import box
from pathlib import Path
from dotenv import load_dotenv
from langchain.chains.summarize import load_summarize_chain
from src.add_to_JSON import write_json
from src.llm import llm, get_num_tokens
from src.prompt_template import code_summary_prompt, template

#load API key from .env
load_dotenv()

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

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
    summary_prompt = code_summary_prompt(code_str)

    #keep track of tokens used for prompt
    num_tokens_prompt = get_num_tokens(summary_prompt)

    print(f"This prompt, including code, contains {num_tokens_prompt} tokens")
    print("\n")

    if num_tokens_prompt > cfg.CONTEXT_WINDOW: 
        #if number of tokens exceeds context window of model, use "stuff" summarization
        chain = load_summarize_chain(llm, chain_type="stuff")
        summary = chain.invoke(code_str)

    else:            
        #else generate summary using prompt
        summary = llm(summary_prompt)
    
    print(f"File: {path} \n Summary: \n {summary}")
    print("\n")

    num_tokens_output = get_num_tokens(summary)

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