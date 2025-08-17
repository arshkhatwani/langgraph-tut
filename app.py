from typing import Annotated
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio

from langgraph.graph import add_messages, StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from prompts.chatbot import CHATBOT_PROMPT

# Load environment variables from .env file
load_dotenv()

llm = init_chat_model("google_genai:gemini-2.5-flash")


class State(BaseModel):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


server_params = StdioServerParameters(
    command="uvx",
    args=["duckduckgo-mcp-server"],
)


async def chatbot(state: State):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            agent = create_react_agent(llm, tools, prompt=CHATBOT_PROMPT)
            agent_response = await agent.ainvoke({"messages": state.messages})
            return {"messages": agent_response.get("messages")}


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
