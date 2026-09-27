"""LangChain agent for OmniAssist.

A single tool-calling agent: the LLM looks at the user query, decides which of
the three tools to call (policy_search / order_status / calculator), LangChain
executes the tool and feeds the result back, and the loop repeats until the
model has enough information to write the final answer.
"""

import os

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools import calculator, order_status, policy_search


# Load variables from .env
load_dotenv()


SYSTEM_PROMPT = """You are OmniAssist, an autonomous customer-support and operations assistant.

Use the available tools to answer:

- policy_search: ANY question about store policy such as refunds,
  cancellations, shipping, and accounts. Base your answer on the policy
  text returned by this tool. Never invent policy.

- order_status: questions about a specific order. Find the order ID
  (for example ORD1001) and call this tool with it.

- calculator: any arithmetic the user asks for, for example "125 * 8".

You may call several tools in sequence when one tool call is not enough.
For example, check an order status and then look up the cancellation policy.

Keep the final answer short and friendly (1-3 sentences).

If a tool returns nothing useful, say so honestly.
"""


# Built once and reused for every request.
_agent_executor = None


def get_agent_executor() -> AgentExecutor:
    """Create the tool-calling agent and cache it."""

    global _agent_executor

    if _agent_executor is None:

        # Check that the Gemini API key exists.
        if not os.environ.get("GOOGLE_API_KEY"):
            raise RuntimeError(
                "GOOGLE_API_KEY is not set. Add your Gemini API key to .env."
            )

        # Create Gemini LLM.
        llm = ChatGoogleGenerativeAI(
            model=os.environ.get(
                "GEMINI_MODEL",
                "gemini-2.5-flash"
            ),
            temperature=float(
                os.environ.get(
                    "GEMINI_TEMPERATURE",
                    "0"
                )
            ),
            google_api_key=os.environ["GOOGLE_API_KEY"],
        )

        # Prompt given to the agent.
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),

                (
                    "human",
                    "User query: {input}\n"
                    "Keywords from NLTK preprocessing: {keywords}"
                ),

                # Stores tool calls and tool results during the agent loop.
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        # Tools available to the agent.
        tools = [
            policy_search,
            order_status,
            calculator,
        ]

        # Create LangChain tool-calling agent.
        agent = create_tool_calling_agent(
            llm=llm,
            tools=tools,
            prompt=prompt,
        )

        # Executor runs the agent and its tools.
        _agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            return_intermediate_steps=True,
            max_iterations=5,
        )

    return _agent_executor


def run_agent(query: str, keywords: list[str]) -> dict:
    """Run the agent for one query.

    Returns:
        {
            "answer": str,
            "tools_used": list[str]
        }
    """

    result = get_agent_executor().invoke(
        {
            "input": query,
            "keywords": ", ".join(keywords) if keywords else "(none)",
        }
    )

    # Find which tools the agent actually used.
    tools_used: list[str] = []

    for step in result.get("intermediate_steps") or []:

        tool_name = step[0].tool

        if tool_name not in tools_used:
            tools_used.append(tool_name)

    return {
        "answer": result["output"],
        "tools_used": tools_used,
    }