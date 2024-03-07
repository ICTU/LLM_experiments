import json
from pathlib import Path
# import yaml
# import box
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import Docx2txtLoader
from langchain.prompts import ChatPromptTemplate


#load API key from env
load_dotenv()

# # Import config vars
# with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
#     cfg = box.Box(yaml.safe_load(ymlfile))


#prompt template for code summary
architecture_task_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful software architect. Your task is analyzing codebases and writing architecture documentetion."),
        ("user", """"
Instructions:

The you are given a large nested json file containing summaries of a codebase on multiple levels. The highest level is a summary of the entire codebase, followed by summaries of the directories/components it contains. On the lowest level it provides summaries of individual files.
You are also given a template for a software architecture document. First, please analyse both files completely before forming your answers. 

Objective:
         
Please fill in the following sections of the architecture document in Dutch. 

Document sections:
```
- 1 Managementsamenvatting
- 3 Ontwerpbeslissingen
- 5.2.1 Use cases
```


Architecture document:```{document}```


json_nested_summaries:```{json_file}```
"""),
    ]
)

def create_llm(max_tokens=None):
    """initiates an OpenAI chat completions llm"""
    return ChatOpenAI(model="gpt-4-0125-preview", temperature=0.2, max_tokens=max_tokens)

def chat_code_summary_prompt(doc_str, json_str):
    return architecture_task_template.format_messages(document=doc_str, json_file=json_str)

def read_json_as_str(path):
    """Opens json file from filepath and reads as str"""
    with open(path, 'r') as file:
        json_data = json.load(file)
    return str(json_data)

def read_doc_as_str(path):
    """Loads docx file and reads as str"""
    loader = Docx2txtLoader(path)
    return str(loader.load())

def complete_doc_prompt(doc_path, json_path):
    """Formats the doc prompt by filling in the doc strings"""
    doc_str = read_doc_as_str(doc_path)
    json_str = read_json_as_str(json_path)
    return chat_code_summary_prompt(doc_str=doc_str, json_str=json_str)

def get_tokens_from_messages(chat_prompt):
    """Calculates number of tokens in the messages list"""
    llm = create_llm()
    return llm.get_num_tokens_from_messages(chat_prompt)

def llm_arch_call(doc_path, json_path):
    """Calls llm to generate architecture documentation"""
    prompt = complete_doc_prompt(doc_path, json_path)
    num_tokens = get_tokens_from_messages(prompt)
    if num_tokens > 128000:
        return print("Input exceeds model token limit")
    elif num_tokens > 124000:
        max_tokens = 128000-num_tokens
        llm = create_llm(max_tokens=max_tokens)
    else: llm = create_llm()
    return llm.invoke(prompt)

print(llm_arch_call(doc_path="example_files/ICTU-Template-Software-architectuurdocument.docx", json_path="metrics/sum_arch_test.json"))



