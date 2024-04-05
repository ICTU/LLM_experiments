from __future__ import annotations
from typing import TypedDict
from pathlib import Path
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains import LLMChain


load_dotenv()


class User_stories(TypedDict):
     
    fo_doc:Path
    use_case:str
    user_stories:list[User_story]
    comments:str
     

class User_story(BaseModel):
     
    identifier:str = Field(description="unique identifier for the user story, using 2 letters and 4 digits for exampel AA0000.")
    description:str = Field(description="3 word description of user story")
    user_story:str = Field(description="a user story in the following format: As a [description of user], I want [functionality] so that [benefit]")
    acceptance_criteria:list = Field(description="numbered list of acceptance criteria")
    dependencies:list[str] = Field(description="list of user story identifiers that need to be implemented before this user story.")

template = """
    You are given an overview of a functional design (1) which describes the functional operation of an application. This includes a description of who can do what with the application, in the form of use cases. You given the description of a specific use case (2).
    You are also given a list of existing user stories (3) and a a user story format (4) to structure your answer.
         
    Instructions:
    - using the provided context (1 & 2) format the list of user stories (3) using the provided format (4)
    - give your answers in dutch
         
    1. Functional design: ```{functional_design}```
        
    2. Use case: ```{use_case}```
         
    3. Existing user stories: ```{user_stories_list}```

    4. {format_instructions}
         
    User stories:"""


def parser_prompt(template, pydantic_object):
    """Creates prompt template for a custom class json output parser"""
    parser = JsonOutputParser(pydantic_object=pydantic_object)
    return PromptTemplate(
        template=template,
        input_variables=["functional_design", "use_case", "user_stories_list"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )


def create_parser_chain(llm, template=template, pydantic_object=User_story):
    """Creates a chain that parses output in json format for a custom class"""
    prompt = parser_prompt(template=template, pydantic_object=pydantic_object)
    parser = JsonOutputParser(pydantic_object=pydantic_object)
    return LLMChain(llm=llm, prompt=prompt, output_key="user_story_json", output_parser=parser)
