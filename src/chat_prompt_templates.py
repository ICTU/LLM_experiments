from langchain_core.prompts import ChatPromptTemplate

chat_code_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and consisely summarizing code files."),
        ("user", "Provide a summary for the following code file, don't include generalities, focus on specifics, file name: {file_name}, code: {code}"),
    ]
)

chat_sum_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and consisely summarizing codebases."),
        ("""The following is a list of summaries describing part of a codebase. 
         
        Component name: {component}
        Summaries: ```{summaries}```
         
        Based on the list of summaries, distil a general description. Explain how it functions like you would to somebody with limited programming knowledge. 
        Helpful Answer:"""),
    ]
)

one_shot_code_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and consisely summarizing code files."),
        ( """user", "Provide a summary for the following code file, don't include generalities, focus on specifics.
        file name: ###EXAMPLE FILENAME
        code: ```###EXAMPLE CODE```"""),
        ("ai", "....."), ###input correct summary here
        ( """user", "Provide a summary for the following code file, don't include generalities, focus on specifics.
        file name: {file_name}
        code: ```{code}```"""),
    ]
)

one_shot_sum_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and consisely summarizing codebases."),
        ("user", """The following is a list of summaries describing part of a codebase. 
         
         Component name: api_server
         Summaries: ['The codebase consists of different components that help automate tasks related to managing Python packages, checking code quality, and handling data in a MongoDB database. These components are like specialized tools that perform specific tasks, such as updating package requirements, running code analysis, managing data models, creating reports, and setting up a Python API server. The components work together to ensure that the code is of good quality, secure, and functions correctly in various scenarios. Overall, the codebase is structured to efficiently organize and streamline the management of data and operations within the software application.', 'The `api_server` component in the codebase sets up a Python API server using Docker. It installs necessary dependencies, creates a virtual environment, and sets up the environment in two stages. The code specifies dependencies for the project, including libraries like Bottle, Cryptography, and Requests. It also includes optional development tools like Mypy and Bandit. The code file "components" is related to the Quality-time API server and provides detailed information in the software documentation.']
         
         Based on the list of summaries, distil a general description. Explain how it functions like you would to somebody with limited programming knowledge. 
         Helpful Answer:"""),
        ("ai", "......."), ###input correct summary here
        ("user","""The following is a list of summaries describing part of a codebase. 
         
         Component name: {component}
         Summaries: {summaries}
         
         Based on the list of summaries, distil a general description. Explain how it functions like you would to somebody with limited programming knowledge. 
         Helpful Answer:"""),
    ]
)

def chat_code_summary_prompt(file_name, code):
    return chat_code_summary_template.format_messages(file_name=file_name, code=code)

def chat_sum_summary_prompt(component, summaries):
    return chat_sum_summary_template.format_messages(component=component, summaries=summaries)