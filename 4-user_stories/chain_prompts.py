from langchain.prompts import PromptTemplate

def user_story_prompt():
    return PromptTemplate(input_variables=['functional_design', 'use_case', 'user_stories_list'], template=user_story_template)

user_story_template = """
    You are given an overview of a functional design which describes the functional operation of an application. This includes a description of who can do what with the application, in the form of use cases. 
    You are also given a user story format and list of existing user stories.
         
    Instructions:
    - using the provided context form 2 new user stories
    - use the provided user story format
    - avoid overlap with the existing user stories (if the list is empty, provide the most basic user stories)
         
    Functional design document: ```{functional_design}```
        
    Use case: ```{use_case}```
        
    User story format: As a [description of user], I want [functionality] so that [benefit]
         
    Existing user stories: ```{user_stories_list}```
         
    User stories:
"""





def criteria_prompt():
    return PromptTemplate(input_variables=['user_stories'], template=criteria_template)

criteria_template = """
Step 2:

For each of the two proposed user stories, add several acceptance criteria. These are defined as Acceptance criteria for user stories are the conditions a product, service, or feature must fulfill for the customer, user, stakeholders, or other systems to accept. They are pre-established standards or requirements that a product or function must meet to satisfy the users’ or stakeholders’ expectations. They define how each system component should work in a given scenario from the end user’s perspective and are unique for each case.

User stories: {user_stories}

Return your answers in the following format:

Description: [3 word description of user story]

User story: As a [description of user], I want [functionality] so that [benefit]

Acceptance criteria: [number list of criteria]
"""

def evaluate_prompt():
    return PromptTemplate(input_variables=['criteria'], template=deepen_template)

deepen_template = """
Step 3:

For each user story and its acceptance criteria consider their pros and cons, initial effort needed, implementation difficulty, and potential challenges.

{criteria}

Evaluations:"""

def summarize_prompt():
    return PromptTemplate(input_variables=['evaluation'], template=rank_solutions_template)

rank_solutions_template = """
Step 4:

Compare the created user stories, their acceptance criteria and evaluations of these user stories to the functional design and the existing list of user stories.
Consider:
- is the user story well defined?
- is the user story a valuable addition to the existing list of user stories?
- summarize your findings

{evaluation}

Summary:"""