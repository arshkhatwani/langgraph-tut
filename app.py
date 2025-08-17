from dotenv import load_dotenv

load_dotenv()

import asyncio

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

from agents.chatbot import chatbot
from models import State


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()


async def stream_graph_updates(user_input: str):
    async for event in graph.astream({"messages": [HumanMessage(content=user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


async def main():
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            await stream_graph_updates(user_input)
        except:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            await stream_graph_updates(user_input)
            break


if __name__ == "__main__":
    asyncio.run(main())
