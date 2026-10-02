"""LangChain tool-calling agent for OmniAssist."""

import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools import calculator, order_status, policy_search

load_dotenv()

SYSTEM_PROMPT = """You are OmniAssist, an autonomous customer-support and operations assistant.

Use the available tools to answer:
- policy_search: ANY question about store policy such as refunds, cancellations, shipping, and accounts. Base your answer on the returned policy text. Never invent policy.
- order_status: questions about a specific order. Find the order ID (for example ORD1001) and call this tool.
- calculator: any arithmetic the user asks for.

You may call several tools in sequence when needed. Keep the final answer short and friendly (1-3 sentences). If a tool returns nothing useful, say so honestly.
"""

_agent_executor = None

def get_agent_executor() -> AgentExecutor:
    global _agent_executor
    if _agent_executor is None:
        if not os.environ.get("GOOGLE_API_KEY"):
            raise RuntimeError("GOOGLE_API_KEY is not set. Add your Gemini API key to .env.")
        llm = ChatGoogleGenerativeAI(
            model=os.environ.get("GEMINI_MODEL", "gemini-3.8-flash"),
            temperature=float(os.environ.get("GEMINI_TEMPERATURE", "0")),
            google_api_key=os.environ["GOOGLE_API_KEY"],
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "User query: {input}\nKeywords from NLTK preprocessing: {keywords}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        tools = [policy_search, order_status, calculator]
        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
        _agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=False,
            return_intermediate_steps=True, max_iterations=5,
        )
    return _agent_executor

def run_agent(query: str, keywords: list[str]) -> dict:
    result = get_agent_executor().invoke({
        "input": query,
        "keywords": ", ".join(keywords) if keywords else "(none)",
    })
    tools_used = []
    for step in result.get("intermediate_steps") or []:
        tool_name = step[0].tool
        if tool_name not in tools_used:
            tools_used.append(tool_name)
    return {"answer": result["output"], "tools_used": tools_used}
