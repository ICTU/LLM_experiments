from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
from src.llm import create_llm
from docs.use_cases import use_cases

summary_path = "doc_summaries.txt"


def read_doc_as_str(path:Path):
    """Loads docx file and reads as str"""
    loader = Docx2txtLoader(path)
    return str(loader.load())


def write_to_file(text:str, file_path:Path):
    """Writes text string to a designated file"""
    with open(file_path, "w") as text_file:
        print(text, file=text_file)


doc_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful functional design assistant."),
        ("user", """You are given 3 documents. 1 is a a functional design document which broadly describes proposed the functional operation of an application. 2 is an architecture document for this application. 3 is a specific use case from the functional design document.
        Your objective is to provide a summary of the proposed application focused on functionality (as described in doc 1 & 2). The goal of the summary is that it can be used to construct user stories the given use case 3, so make sure the summary contains information useful to achieving that goal.
        
         
        1. Functional design document: ```{functional_design}```
        
        2. User story examples: ```{architecture_doc}```
        
        3. Use case: ```{use_case}``` 
        
        Summary:"""),
    ]
)


doc_summary_template_simple = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful functional design assistant."),
        ("user", """You are given a functional design document which broadly describes proposed the functional operation of an application.
        Your objective is to provide a summary of the proposed application focused on functionality. The goal of the summary is that it can be used to construct user stories for the included use cases, so make sure the summary contains information useful to achieving that goal.
        
        Functional design document: ```{functional_design}```
        
        Summary:"""),
    ]
)


def doc_summary_prompt(fo_doc:str, sad_doc:str, use_case:str):
    return doc_summary_template.format_messages(functional_design=fo_doc, architecture_doc=sad_doc, use_case=use_case)


def doc_summary_prompt_simple(fo_doc:str):
    return doc_summary_template_simple.format_messages(functional_design=fo_doc)


def summarize_docs(fo_doc:Path, sad_doc:Path, use_case):
    """Summarizes project documents with regard to a specific use case"""
    fo_text = read_doc_as_str(fo_doc)
    sad_text = read_doc_as_str(sad_doc)
    llm = create_llm()
    prompt = doc_summary_prompt(fo_text, use_case, sad_text)
    summary = llm.invoke(prompt)
    return write_to_file(summary.content, file_path=summary_path), print(summary.content)


def summarize_docs_simple(fo_doc:Path):
    """Summarizes project fo document"""
    fo_text = read_doc_as_str(fo_doc)
    llm = create_llm()
    prompt = doc_summary_prompt_simple(fo_text)
    summary = llm.invoke(prompt)
    return write_to_file(summary.content, file_path=summary_path), print(summary.content)

#summarize_docs(fo_doc="docs/Globaal-Functioneel-Ontwerp InkoopDB.docx", sad_doc="docs/SAD InhuurDB.docx", use_case=use_cases["UC1.3"])

#summarize_docs_simple(fo_doc="docs/Globaal-Functioneel-Ontwerp InkoopDB.docx")