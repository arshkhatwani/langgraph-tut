from typing import Annotated
from pydantic import BaseModel
from dotenv import load_dotenv

from langgraph.graph import add_messages, StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

# Load environment variables from .env file
load_dotenv()

llm = init_chat_model("google_genai:gemini-2.5-flash")


class State(BaseModel):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

def chatbot(state: State):
    return {"messages": [llm.invoke(state.messages)]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [HumanMessage(content=user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break