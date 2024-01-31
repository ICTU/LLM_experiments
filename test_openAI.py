import os 
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

#load API key
load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

#initialize OpenAI model
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, max_tokens=80)

#select code file
def read_code_as_str(code_filepath):
    code_str = code_filepath.read_text()
    return code_str

code_filepath = Path("C:/Users/jeelb/OneDrive - Stichting ICTU/Documenten/Code genAI/quality-time/components/notifier/src/notifier/notifier.py")

code_str = read_code_as_str(code_filepath)

#code summarization prompt template
prompt = PromptTemplate.from_template(
    "Write a genaral summary for the code delineated by the triple backticks, don't go into specifics. Examine the whole code before you form your answer and try to explain it's function in simple terms. Code: ```{code}```"
    )

#set input
prompt_value = prompt.format(code=code_str)

#call llm function
print(llm.invoke(prompt_value))