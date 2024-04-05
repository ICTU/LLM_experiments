from langchain_core.prompts import ChatPromptTemplate
from src.llm import create_llm


def translate_to_dutch(input):
    llm = create_llm()
    prompt = translate_prompt(input)
    print("Translating to dutch...")
    return llm.invoke(prompt).content        


translate_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful and precise translation assistant."),
        ("user", """You are given a list of user stories written in English. Please translate it to Dutch. 
        
        User stories: ```{user_story}```
        
        Translation:"""),
    ]
)


def translate_prompt(item):
    return translate_template.format_messages(user_story=item)