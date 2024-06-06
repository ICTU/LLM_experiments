import os
import json
from dotenv import load_dotenv
from typing import Annotated, Literal, Union
from typing_extensions import TypedDict 

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import ToolMessage, BaseMessage
from langchain_community.tools.tavily_search import TavilySearchResults

# load api keys
load_dotenv()

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function in the annotation defines how this state key should be updated
    messages: Annotated[list, add_messages]


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""
    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


def create_tools():
    """Creates a list of tools that can be used by an LLM"""
    search_tool = TavilySearchResults(max_results=2)
    # add more tools here
    tools = [search_tool]
    return tools


def build_llm_with_tools(model="claude-3-haiku-20240307"):
    """Creates a LLM and binds it with a list of tools"""
    tools = create_tools()
    llm = ChatAnthropic(model=model)
    return llm.bind_tools(tools)


def chatbot(state: State):
    """Calls an LLM using a graph state"""
    llm = build_llm_with_tools()
    return {"messages": [llm.invoke(state["messages"])]}


def route_tools(
state: State,
) -> Literal["tools", "__end__"]:
    """Use in the conditional_edge to route to the ToolNode if the last message

    has tool calls. Otherwise, route to the end."""
    # The `route_tools` function returns "tools" if the chatbot asks to use a tool, and "__end__" if
    # it is fine directly responding. This conditional routing defines the main agent loop.
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"

#build the graph
def build_chatbot_graph():
    memory = SqliteSaver.from_conn_string(":memory:")

    graph_builder = StateGraph(State)
    
    graph_builder.add_node("chatbot", chatbot)

    tool_node = ToolNode(tools=create_tools())
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
    
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("chatbot")
    #graph_builder.set_finish_point("chatbot")

    return graph_builder.compile(checkpointer=memory)


def create_graph_image(graph:CompiledStateGraph, image_path = 'graph_visual.png'):
    """Creates a schematic image of the compiled graph"""
    image_data = graph.get_graph().draw_mermaid_png()
    with open(image_path, 'wb') as f:
        f.write(image_data)


if __name__ == "__main__":

    chatbot_graph = build_chatbot_graph()
    
    # create image of graph
    create_graph_image(chatbot_graph)


    # while True:
    #     user_input = input("User: ")
    #     if user_input.lower() in ["quit", "exit", "q"]:
    #         print("Goodbye!")
    #         break
    #     for event in chatbot_graph.stream({"messages": [("user", user_input)]}):
    #         for value in event.values():
    #             if isinstance(value["messages"][-1], BaseMessage):
    #                 print("Assistant:", value["messages"][-1].content)
    