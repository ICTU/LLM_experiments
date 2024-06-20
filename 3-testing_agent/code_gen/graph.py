import sys
from typing import Dict, TypedDict, List
# from operator import itemgetter
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph
from llm import code_gen_chain
from load_docs import concatenated_content, functionality, unit_test
from langgraph.graph.state import CompiledStateGraph

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        error : Binary flag for control flow to indicate whether test error was tripped
        messages : With user question, error messages, reasoning
        generation : Code solution
        iterations : Number of tries
    """

    error: str
    messages: List
    generation: str
    iterations: int


    ### Parameter

# Max tries
max_iterations = 5
    # Reflect
# flag = 'reflect'
flag = "do not reflect"

### Nodes


def generate(state: GraphState):
    """
    Generate a code solution

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation
    """

    print("---GENERATING CODE SOLUTION---")

    # State
    messages = state["messages"]
    iterations = state["iterations"]
    error = state["error"]

    # We have been routed back to generation with an error
    if error == "yes":
        messages += [
            (
                "user",
                "Now, try again. Invoke the code tool to structure the output with a prefix, imports, and code block:",
            )
        ]

    # Solution
    code_solution = code_gen_chain.invoke(
        {"codefiles": concatenated_content, "messages": messages}
    )
    messages += [
        (
            "assistant",
            f"{code_solution.prefix} \n Imports: {code_solution.imports} \n Code: {code_solution.code}",
        )
    ]

    # Increment
    iterations = iterations + 1
    return {"generation": code_solution, "messages": messages, "iterations": iterations}


def code_check(state: GraphState):
    """
    Check code

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, error
    """

    print("---CHECKING CODE---")

    # State
    messages = state["messages"]
    code_solution = state["generation"]
    iterations = state["iterations"]

    # Get solution components
    prefix = code_solution.prefix
    imports = code_solution.imports
    code = code_solution.code

    # Check imports
    try:
        exec(imports)
    except Exception as e:
        error_message = [("user", f"Your solution failed the import test: {e}")]
        print("---CODE IMPORT CHECK: FAILED---", error_message)
        messages += error_message
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": "yes",
        }

    # Check execution
    all_code = imports + "\n" + code
    with open("test.py", "w") as fd:
        fd.write(all_code)
    try:
        import os
        os.subprocess(["python", "test.py"])
    except Exception as e:
        print("---CODE BLOCK CHECK: FAILED---")
        error_message = [("user", f"Your solution failed the code execution test: {e}")]
        messages += error_message
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": "yes",
        }

    # No errors
    print("---NO CODE TEST FAILURES---")
    return {
        "generation": code_solution,
        "messages": messages,
        "iterations": iterations,
        "error": "no",
    }


def reflect(state: GraphState):
    """
    Reflect on errors

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation
    """

    print("---GENERATING CODE SOLUTION---")

    # State
    messages = state["messages"]
    iterations = state["iterations"]
    code_solution = state["generation"]

    # Prompt reflection
    reflection_message = [
        (
            "user",
            """You tried to solve this problem and failed a unit test. Reflect on this failure
                                    given the provided documentation. Write a few key suggestions based on the 
                                    documentation to avoid making this mistake again.""",
        )
    ]

    # Add reflection
    reflections = code_gen_chain.invoke(
        {"codefiles": concatenated_content, "messages": messages}
    )
    messages += [("assistant", f"Here are reflections on the error: {reflections}")]
    return {"generation": code_solution, "messages": messages, "iterations": iterations}


### Edges

def decide_to_finish(state: GraphState):
    """
    Determines whether to finish.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    error = state["error"]
    iterations = state["iterations"]

    if error == "no" or iterations == max_iterations:
        print("---DECISION: FINISH---")
        # print(f"---FINAL SOLUTION--- {st}")
        return "end"
    else:
        print("---DECISION: RE-TRY SOLUTION---")
        if flag == "reflect":
            return "reflect"
        else:
            return "generate"
        

def create_graph():
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("generate", generate)  # generation solution
    workflow.add_node("check_code", code_check)  # check code
    workflow.add_node("reflect", reflect)  # reflect

    # Build graph
    workflow.set_entry_point("generate")
    workflow.add_edge("generate", "check_code")
    workflow.add_conditional_edges(
        "check_code",
        decide_to_finish,
        {
            "end": END,
            "reflect": "reflect",
            "generate": "generate",
        },
    )
    workflow.add_edge("reflect", "generate")
    return workflow.compile()

def create_graph_image(graph:CompiledStateGraph, image_path = 'graph_visual.png'):
    """Creates a schematic image of the compiled graph"""
    image_data = graph.get_graph().draw_mermaid_png()
    with open(image_path, 'wb') as f:
        f.write(image_data)


if __name__ == "__main__":

    app = create_graph()
    create_graph_image(app)

    question =  f"""Please improve upon the given unit test to test the specified functionality in the codebase.

    Carefully analyze the provided codefiles and identify the key components, functions, and classes that are directly related to implementing the specified functionality. 

    Then, write a comprehensive set of unit tests in the same programming language as the codebase. Make sure your tests are thorough and cover as many potential issues as possible. The goal is to catch any bugs or unintended behavior related to the specified functionality.

    Your tests should be focused specifically on:
        
    <functionality>
    {functionality}
    </functionality>

    Do not worry about testing unrelated parts of the codebase.

    Here is the existing unit test code that you should use as a starting point and extend upon. Your tests should be compatible with this existing codebase and should be written in the same programming language and testing framework.
    
    Return the existing test and your additional tests. Add 'unittest.main()' as the last line. Don't include if __name__  == '__main__': in your solution.
    <unit_test>
    {unit_test}
    </unit_test>""" 

    app.invoke({"messages": [("user", question)], "iterations": 0})
    print(f"---FINAL SOLUTION--- {app.get_state['generation']}")



