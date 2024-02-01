import os
import pathlib
from langchain_openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, max_tokens=100)


def summarize_file(file_name):
    with file_name.open() as code_file:
        summary = llm(code_file.read())
        print(summary)


for (path, dirs, files) in pathlib.Path("C:/Users/jeelb/OneDrive - Stichting ICTU/Documenten/Code genAI/quality-time/components/notifier/src/").walk():
    for file in files:
        print(path)
        summarize_file(path/file)
        