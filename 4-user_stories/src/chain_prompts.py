from langchain.prompts import PromptTemplate


def user_story_prompt():
    return PromptTemplate(input_variables=['functional_design', 'use_case', 'user_stories_list'], template=user_story_template)


user_story_template = """
    You are given an overview of a functional design (1) which describes the functional operation of an application. This includes a description of who can do what with the application, in the form of use cases. You given the description of a specific use case (2).
    You are also given a list of existing user stories (3) and a a user story format (4) to structure your answer.
         
    Instructions:
    - using the provided context (1) form a new user story for the use case (2)
    - avoid overlap with the existing user stories (3) (if the list is empty, provide the most basic user story)
    - use the provided user story format (4)
         
    1. Functional design: ```{functional_design}```
        
    2. Use case: ```{use_case}```
         
    3. Existing user stories: ```{user_stories_list}```

    4. Give your answer using this user story format: As a [description of user], I want [functionality] so that [benefit]
         
    User stories:
"""



def criteria_prompt():
    return PromptTemplate(input_variables=['user_stories'], template=criteria_template)

criteria_template = """
For each new user story add 5 acceptance criteria. These are defined as the conditions a product, service, or feature must fulfill for the customer, user, stakeholders, or other systems to accept. They are pre-established standards or requirements that a product or function must meet to satisfy the users’ or stakeholders’ expectations. They define how each system component should work in a given scenario from the end user’s perspective and are unique for each case.

User stories: {user_stories}

Return your answers in the following json format (use the existing keys, fill in the values):

'description': [3 word description of user story],
'user_story': As a [description of user], I want [functionality] so that [benefit],
'acceptance_criteria': [numbered list of criteria])

json format user story:"""