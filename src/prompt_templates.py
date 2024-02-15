from langchain.prompts import PromptTemplate

#regular summary templates
code_template = """
    Write a concise summary for the code delineated by the triple backticks. Don't include generalities, focus on specifics.
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

    Based on this list of summaries, provide a consice summary of the component. Don't include generalities, focus on specifics."""

def summaries_summary_prompt(name, summaries):
    """function to fill the summaries summary template, takes the component name and summaries as input"""
    prompt = PromptTemplate(input_variables=["component", "summaries"], template=summaries_template)
    summary_prompt = prompt.format(component=name, summaries=summaries)
    return summary_prompt

#chain templates
map_template = """"The following is a set of summaries describing a parts of a codebase component.
Summaries: {text}

Based on the list of summaries, distil a general description of the component
Helpful Answer:
"""

map_prompt = PromptTemplate(input_variables=['text'], template=map_template)

reduce_template = """The following list of summaries delineated by triple backticks describes files and directories forming a codebase component.
    List of Summaries: ```{text}```

    Take these summaries and distill them into a final consolidated summary of the component.
    Helpful answer:"""

reduce_prompt = PromptTemplate(input_variables=['text'], template=reduce_template)