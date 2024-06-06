from langchain_core.prompts import ChatPromptTemplate

#regular chat prompt templates
chat_code_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and concisely summarizing code files."),
        ("user", "Provide a summary for the following code file, don't include generalities, focus on specifics, file name: {file_name}, code: {code}"),
    ]
)

chat_sum_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and concisely summarizing codebases."),
        ("""The following is a list of summaries describing part of a codebase. 
         
        Component name: {component}
        Summaries: ```{summaries}```
         
        Based on the list of summaries, distil a general description. Explain how it functions like you would to somebody with limited programming knowledge. 
        Helpful Answer:"""),
    ]
)


#one-shot templates include a single example for the model to follow
one_shot_code_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and concisely summarizing code files."),
        ( "user", """Provide a summary for the following code file, don't include generalities, focus on specifics. Keep your answer short and concise (max 100 words).
        file name: {example_name}
        code: ```{example_code}
```"""),
        ("ai", """{example_answer}"""),
        ( "user", """Provide a summary for the following code file, don't include generalities, focus on specifics. Keep your answer short and concise (max 100 words) and follow the the same structure as your previous answer,.
        file name: {file_name}
        code: ```{code}```"""),
    ]
)

one_shot_sum_summary_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful code expert. Your task is analyzing, and concisely summarizing codebases."),
        ("user", """The following is a list of summaries describing part of a codebase. 
         
         Component name: {example_component}
         Summaries: {example_summaries}
         
         Based on the list of summaries, distil a general description. Explain how it functions like you would to somebody with limited programming knowledge. Keep your answers factual and short, no yapping. 
         Helpful Answer:"""),
        ("ai", ".{example_answer}"), ###input correct summary here
        ("user","""The following is a list of summaries describing part of a codebase. 
         
         Component name: {component}
         Summaries: {summaries}
         
         Based on the list of summaries, distil a general description. Explain how it functions like you would to somebody with limited programming knowledge. Keep your answers factual, short (max 120 words) and follow the the same structure as your previous answer, no yapping.
         Helpful Answer:"""),
    ]
)


#dictionaries containing examples for one shot prompt
one_shot_code_example = {
    'answer': """
    **What it does**: provides a React component that lets the user select a subject type for a subject in a quality report.

    **How it does it**: wraps the widget for single choice inputs with the subject types available in the data model.""",
    'file_name': 'SubjectType.js',
    'code':"""import React, { useContext } from 'react';
import { Header } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';

export function subjectTypes(dataModel) {
    let options = [];
    Object.keys(dataModel.subjects).forEach((key) => {
        const option_subject_type = dataModel.subjects[key];
        options.push({
            key: key, text: option_subject_type.name, value: key,
            content: <Header as="h4" content={option_subject_type.name} subheader={option_subject_type.description} />
        });
    });
    return options;
}

export function SubjectType({ subject_type, set_value }) {
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Subject type"
            options={subjectTypes(useContext(DataModel))}
            set_value={(value) => set_value(value)}
            value={subject_type}
        />
    );
}"""
}

one_shot_sum_example = {
    'answer': """
    **What it does**: provides the user interface of Quality-time that users can access in their browser. The user interface allows users to create and configure Quality-reports and view the current and historical status of metrics.

    **How it does it**: bundles the React components into a runtime Docker component that serves the bundled Javascript and HTML for the Quality-time application.""",
    'component_name': 'frontend',
    'summaries': """["The \"public\" component in this codebase is an HTML file that serves as a basic template for a web application. It includes important information for the web app, like character encoding, viewport settings, and theme color. It also links to a favicon and a manifest file for Android homescreen integration. The file uses a placeholder `%PUBLIC_URL%` for paths that will be filled in during the building process. It includes a message for users who don't have JavaScript enabled and a main div for displaying content. Additionally, it provides instructions for development. Overall, this file sets up the foundation for the web application and ensures it functions correctly across different devices and platforms.", "The codebase consists of different components that work together to create a web application. Each component has a specific role, such as managing communication with a server, displaying changelog information, handling user interactions on a dashboard, managing input fields, controlling the appearance of headers and footers, and more. \n\nThese components help in tasks like tracking and displaying issues, handling and displaying metrics and measurements, managing notifications, creating and handling reports, and sharing content on webpages. The codebase also includes tools for testing to ensure everything works correctly.\n\nOverall, the codebase is like a toolbox with different parts that help in building and maintaining a web application, making it easier for users to interact with data, settings, and features on the website.", "The frontend component of the codebase sets up the environment for a frontend application using Node.js. It installs necessary tools, copies files, and defines commands to run the application. It also includes scripts for managing a React project, such as starting the app, running tests, and building for production. Additionally, it contains components for the user interface, likely used for creating interactive elements and displaying information to the user."]"""
}

def chat_code_summary_prompt(file_name, code):
    return chat_code_summary_template.format_messages(file_name=file_name, code=code)

def chat_sum_summary_prompt(component, summaries):
    return chat_sum_summary_template.format_messages(component=component, summaries=summaries)

def one_shot_code_summary_prompt(file_name, code):
    example_name = one_shot_code_example["file_name"]
    example_code = one_shot_code_example["code"]
    example_answer = one_shot_code_example["answer"]
    return one_shot_code_summary_template.format_messages(
                                            file_name=file_name,
                                            code=code,
                                            example_name=example_name,
                                            example_code=example_code,
                                            example_answer=example_answer)

def one_shot_sum_summary_prompt(component, summaries):
    example_component = one_shot_sum_example["component_name"]
    example_summaries = one_shot_sum_example["summaries"]
    example_answer = one_shot_sum_example["answer"]
    return one_shot_sum_summary_template.format_messages(
                                            component=component,
                                            summaries=summaries,
                                            example_component=example_component,
                                            example_summaries=example_summaries,
                                            example_answer=example_answer)