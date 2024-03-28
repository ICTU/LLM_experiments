from langchain_core.prompts import ChatPromptTemplate
from src.llm import create_llm


def evaluate_user_stories(input:list, fo_summary:str, use_case:str) -> list:
    llm = create_llm()
    prompt = evaluate_prompt(input=input, fo_summary=fo_summary, use_case=use_case)
    return llm.invoke(prompt).content


evaluate_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful and precise product owner."),
        ("user", """You are given a summary of the functional design for an application (1), a specific use case for this application (2) and a list of user stories for this use case (3)
        Please evaluate the list of user stories. Check if there are user stories that overlap or if there are stories that depend on other user stories. Adjust the list where necessary. 
        
        1. Functional design: ```{fo_summary}```
        
        2. Use case: ```{use_case}``
         
        3. List of user stories: ```{user_stories}```
        
        Return ONLY the adjusted list of user stories.
         
        List:"""),
    ]
)


def evaluate_prompt(input, fo_summary, use_case):
    return evaluate_template.format_messages(user_stories=input, fo_summary=fo_summary, use_case=use_case)