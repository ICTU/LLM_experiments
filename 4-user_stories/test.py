from langchain_community.document_loaders import Docx2txtLoader
from src.llm import create_llm, get_num_tokens
from src.prompts import user_story_prompt, use_case_prompt

def read_doc_as_str(path):
    """Loads docx file and reads as str"""
    loader = Docx2txtLoader(path)
    return str(loader.load())

def fill_user_story_prompt(doc_path, use_case):
    """Formats the doc prompt by filling in the doc strings"""
    doc_str = read_doc_as_str(doc_path)
    if use_case == True:
        return use_case_prompt(FO_doc=doc_str)
    else: 
        return user_story_prompt(FO_doc=doc_str)

def generate_user_stories(doc_path, use_case):
    llm = create_llm()
    prompt = fill_user_story_prompt(doc_path=doc_path, use_case=use_case)
    return llm.invoke(prompt)


print(generate_user_stories("docs/Globaal-Functioneel-Ontwerp InkoopDB.docx", use_case=True).content)

# print(get_num_tokens(fill_user_story_prompt("docs/Globaal-Functioneel-Ontwerp InkoopDB.docx")))