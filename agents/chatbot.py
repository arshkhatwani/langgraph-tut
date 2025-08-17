from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from models import State
from langchain.chat_models import init_chat_model
from prompts.chatbot import CHATBOT_PROMPT

# Initialize the LLM and prompt
llm = init_chat_model("google_genai:gemini-2.5-flash")

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
