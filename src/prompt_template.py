from langchain.prompts import PromptTemplate

code_template = """
    Write a concise summary for the code delineated by the triple backticks. 
    File name: {file_name}
    Code: ```{code}```
"""

def code_summary_prompt(name, code_str):
    """function to fill the code summary template, takes the file name and code as input"""
    prompt = PromptTemplate(input_variables=["file_name", "code"], template=code_template)
    summary_prompt = prompt.format(file_name=name, code=code_str)
    return summary_prompt

summaries_template = """The following list of summaries delineated by triple backticks describes files and directories forming a codebase component.
    Component name: {component}
    List of Summaries: ```{summaries}```
    
    Based on this list of summaries, provide a consice summary of the component."""

def summaries_summary_prompt(name, summaries):
    prompt = PromptTemplate(input_variables=["component", "summaries"], template=summaries_template)
    summary_prompt = prompt.format(component=name, summaries=summaries)
    return summary_prompt