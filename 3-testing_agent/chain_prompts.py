from langchain.prompts import PromptTemplate

def solutions_prompt():
    return PromptTemplate(input_variables=['input', 'perfect_factors'], template=solutions_template)

solutions_template = """
Step1 :
 
I have a problem related to {input}. Could you brainstorm three distinct solutions? Please consider a variety of factors such as {perfect_factors}
A:
"""

def evaluate_prompt():
    return PromptTemplate(input_variables=['solutions'], template=evaluate_template)

evaluate_template = """
Step 2:

For each of the three proposed solutions, evaluate their potential. Consider their pros and cons, initial effort needed, implementation difficulty, potential challenges, and the expected outcomes. Assign a probability of success and a confidence level to each option based on these factors

{solutions}

A:"""

def deepen_prompt():
    return PromptTemplate(input_variables=['review'], template=deepen_template)

deepen_template = """
Step 3:

For each solution, deepen the thought process. Generate potential scenarios, strategies for implementation, any necessary partnerships or resources, and how potential obstacles might be overcome. Also, consider any potential unexpected outcomes and how they might be handled.

{review}

A:"""

def rank_prompt():
    return PromptTemplate(input_variables=['deepen_thought_process'], template=rank_solutions_template)

rank_solutions_template = """
Step 4:

Based on the evaluations and scenarios, rank the solutions in order of promise. Provide a justification for each ranking and offer any final thoughts or considerations for each solution
{deepen_thought_process}

A:"""