import os
import json
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict 

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import ToolMessage, BaseMessage, HumanMessage, AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults

# load api keys
load_dotenv()

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function in the annotation defines how this state key should be updated
    messages: Annotated[list, add_messages]


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

    return graph_builder.compile(
        checkpointer=memory,
        interrupt_before=["tools"]
        )


def create_graph_image(graph:CompiledStateGraph, image_path = 'graph_visual.png'):
    """Creates a schematic image of the compiled graph"""
    image_data = graph.get_graph().draw_mermaid_png()
    with open(image_path, 'wb') as f:
        f.write(image_data)


if __name__ == "__main__":

    chatbot_graph = build_chatbot_graph()
    
    # create image of graph
    create_graph_image(chatbot_graph)

    config = {"configurable": {"thread_id": "1"}}

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        #if user input is None, the graph will continue where it left off, without adding anything new to the state
        if user_input.lower() == "none":
            for event in chatbot_graph.stream(
                None,
                config,
                stream_mode="values"
            ):
                for messages in event.values():
                    if isinstance(messages[-1], BaseMessage):
                        if isinstance(messages[-1], AIMessage):
                            print("Assistant:", messages[-1].content)                
        for event in chatbot_graph.stream(
            {"messages": [("user", user_input)]},
            config,
            stream_mode="values"
        ):
            for messages in event.values():
                if isinstance(messages[-1], BaseMessage):
                    if isinstance(messages[-1], AIMessage):
                        print("Assistant:", messages[-1].content)
    
    #use to check state of graph for thread id (config)
    snapshot = chatbot_graph.get_state(config)
    print(snapshot)
    print(snapshot.next)
