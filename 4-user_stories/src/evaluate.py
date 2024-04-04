from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from src.llm import create_llm

def fill_prompt(template, fo_summary, use_case, user_stories):
    return template.format_messages(fo_summary=fo_summary, use_case=use_case, user_stories_list=user_stories)

def generate_comments(user_stories, fo_summary:str, use_case:str, role:str):
    """Evaluates the user stories from the viewpoint of a specifiec development role.
    
    :param role: role of the evaluator, support "po", "dev"
    """
    print(f"{role} evaluating user stories...")
    llm = create_llm()
    if role == "po":
        prompt = fill_prompt(template=evaluate_template_po, fo_summary=fo_summary, use_case=use_case, user_stories=user_stories)
    if role == "dev":
        prompt = fill_prompt(template=evaluate_template_dev, fo_summary=fo_summary, use_case=use_case, user_stories=user_stories)
    return llm.invoke(prompt).content

evaluate_template_po = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful and precise product owner."),
        ("user", """You are given a summary of the functional design for an application (1), a specific use case for this application (2) and a list of user stories for this use case (3).
        Please evaluate the list of user stories. Check if there are user stories that overlap or if there are stories that depend on other user stories. For each user story and its acceptance criteria consider their pros and cons. Be very strict.
        
        1. Functional design: ```{fo_summary}```
        
        2. Use case: ```{use_case}``
         
        3. List of user stories: ```{user_stories_list}```
         
        Comments:"""),
    ]
)


evaluate_template_dev = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a software developer working on an application."),
        ("user", """You are given a summary of the functional design for an application (1), a specific use case for this application (2) and a list of user stories for this use case (3).
        Please evaluate the list of user stories. Provide feedback on whether they are formulated clearly enough to work with as a developer.
        
        1. Functional design: ```{fo_summary}```
        
        2. Use case: ```{use_case}``
         
        3. List of user stories: ```{user_stories_list}```
         
        Comments:"""),
    ]
)


def evaluate_prompt_po():
    return PromptTemplate(input_variables=['functional_design', 'use_case', 'user_stories_list'], template=evaluate_template_po_chain)

evaluate_template_po_chain = """You are a helpful and precise product owner. You are given a summary of the functional design for an application (1), a specific use case for this application (2) and a list of user stories for this use case (3).
        Please evaluate the list of user stories. Check if there are user stories that overlap or if there are stories that depend on other user stories. For each user story and its acceptance criteria consider their pros and cons, initial effort needed, implementation difficulty, and potential challenges. 
        
        1. Functional design: ```{functional_design}```
        
        2. Use case: ```{use_case}``
         
        3. List of user stories: ```{user_stories_list}```
         
        Comments:"""

def evaluate_prompt_dev():
    return PromptTemplate(input_variables=['po_comments'], template=evaluate_template_dev_chain)

evaluate_template_dev_chain = """You are a software developer working on an application. Add to the work of the product owner with your own evaluations. Provide feedback on whether the user stories are formulated clearly enough to work with as a developer. Return both the comments of the PO and your own thoughts.
        
        Comments product owener: {po_comments}
         
        Comments:"""