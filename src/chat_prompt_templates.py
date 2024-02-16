from langchain_core.prompts import ChatPromptTemplate

chat_code_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and consisely summarizing code files."),
        ("user", "Provide a summary for the following code file, don't include generalities, focus on specifics, file name: {file_name}, code: {code}"),
    ]
)

chat_sum_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and consisely summarizing code components."),
        ("""The following is a list of summaries describing a parts of a codebase component. 
         
         Component name: {component}
         Summaries: {summaries}
         
         Based on the list of summaries, distil a general description of the component. 
         Helpful Answer:"""),
    ]
)

def chat_code_summary_prompt(file_name, code):
    return chat_code_summary_template.format_messages(file_name=file_name, code=code)

def chat_sum_summary_prompt(component, summaries):
    return chat_sum_summary_template.format_messages(component=component, summaries=summaries)

print(chat_code_summary_template)