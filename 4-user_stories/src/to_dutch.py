from langchain_core.prompts import ChatPromptTemplate
from src.llm import create_llm


def translate_to_dutch(input:list) -> list:
    llm = create_llm()
    output = []
    for item in input:
        prompt = translate_prompt(item)
        output.append(llm.invoke(prompt).content)
    return output
        


translate_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful and precise translation assistant."),
        ("user", """You are given a user story written in English. Please translate it to Dutch. 
        
        User story: ```{user_story}```
        
        Translation:"""),
    ]
)


def translate_prompt(item):
    return translate_template.format_messages(user_story=item)