import os
from openai import OpenAI
from uuid import uuid4
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def reduce_messages(left: list[AnyMessage], right: list[AnyMessage]) -> list[AnyMessage]:
    # assign ids to messages that don't have them
    for message in right:
        if not message.id:
            message.id = str(uuid4())
    # merge the new messages with the existing messages
    merged = left.copy()
    for message in right:
        for i, existing in enumerate(merged):
            # replace any existing messages with the same id
            if existing.id == message.id:
                merged[i] = message
                break
        else:
            # append any new messages to the end
            merged.append(message)
    return merged

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], reduce_messages]


class Agent:
    def __init__(self, model, tools, checkpointer, system_message=""):
        self.system = system_message
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_open_ai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile(
            checkpointer=checkpointer,
            interrupt_before=["action"]
            )
        self.tools = {tool.name: tool for tool in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state:AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_open_ai(self, state: AgentState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {"messages": [message]}
    
    def take_action(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for tool in tool_calls:
            print(f"Callng tool: {tool}")
            result = self.tools[tool['name']].invoke(tool['args'])
            results.append(ToolMessage(tool_call_id=tool['id'], name=tool['name'], content=str(result)))
            print(f"Tool result: {result}")
        print("Returning to model...")
        return {"messages": results}
    

memory = SqliteSaver.from_conn_string(":memory:")

prompt = """You are a smart research assistant. Use the search engine to look up information. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!
"""
tool = TavilySearchResults(max_results=2) #increased number of results
model = ChatOpenAI(model="gpt-3.5-turbo")
abot = Agent(model, [tool], system_message=prompt, checkpointer=memory)

messages = [HumanMessage(content="What is the weather like in Amsterdam?")]

thread = {"configurable": {"thread_id": "1"}}

for event in abot.graph.stream({"messages": messages}, config=thread):
    for value in event.values():
        print(value["messages"])
while abot.graph.get_state(thread).next:
    print("\n", abot.graph.get_state(thread),"\n")
    _input = input("proceed?")
    if _input != "y":
        print("aborting")
        break
    for event in abot.graph.stream(None, thread):
        for v in event.values():
            print(v)


#state modification
messages =  [HumanMessage(content="What is the best private maplestory server?")]
thread = {"configurable": {"thread_id": "3"}}

for event in abot.graph.stream({"messages": messages}, thread):
    for v in event.values():
        print(v)

abot.graph.get_state(thread)

current_values = abot.graph.get_state(thread)
print(current_values.values['messages'][-1])
current_values.values['messages'][-1].tool_calls = [
    {'name': 'tavily_search_results_json', 
     'args': {'query': 'best private Runescape server'}, 
     'id': 'call_Ql6Zs5OxcdrD7g0vg1qskK9P'}
     ]  

abot.graph.update_state(thread, current_values.values)


current_state = abot.graph.get_state(thread)
print(current_state)

for event in abot.graph.stream(None, thread):
    for v in event.values():
        print(v)