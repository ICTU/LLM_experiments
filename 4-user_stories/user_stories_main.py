from __future__ import annotations
import sys
from typing import TypedDict
from pathlib import Path
from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache

from src.summarize_docs import summarize_docs_simple, write_to_file
from sequence_chain import generate_user_stories
from docs.use_cases import use_cases_inkoop


class User_stories(TypedDict):
     
    fo_doc:Path
    use_cases:dict
    user_stories:list[User_story]
     

class User_story(TypedDict):
     
    use_case_key:str
    title:str
    user_story:str
    acceptance_criteria:list
    open_issues:list


def user_stories_main(fo_doc_path:Path, use_cases:dict, no_stories:int, results_path):
    """Uses a design document to generate user stories for a use cases"""
    fo_summary_text = summarize_docs_simple(fo_doc_path=fo_doc_path)
    user_stories_dict = {}
    for key, value in use_cases.items():
        user_stories = generate_user_stories(fo_summary=fo_summary_text, use_case=value, no_stories=no_stories)
        user_stories_dict.update({key: user_stories})
    return write_to_file(user_stories_dict, results_path)

fo_doc_path = "docs/Globaal-Functioneel-Ontwerp InkoopDB.docx"

if __name__ == "__main__":
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))
        #doc_path = Path(sys.argv[1]).resolve(strict=True)
        doc_path = "docs/Globaal-Functioneel-Ontwerp InkoopDB.docx"
        use_cases = use_cases_inkoop
        results_path = "results.py"
        user_stories_main(fo_doc_path=doc_path, use_cases=use_cases_inkoop, no_stories=5, results_path=results_path)