import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="OmniAssist", page_icon="🤖", layout="centered")
st.title("🤖 OmniAssist")
st.caption("Autonomous Customer Support & Operations Assistant")
st.write("Ask about refunds, cancellations, shipping, accounts, orders, or calculations.")

with st.sidebar:
    st.header("About")
    st.write("""
    🧠 Gemini + LangChain

    🔎 ChromaDB RAG

    📝 NLTK preprocessing

    🛠️ Tool calling

    ⚡ FastAPI REST API
    """)
    st.divider()
    st.subheader("Try asking")
    st.write("• What is the refund policy?")
    st.write("• How long does shipping take?")
    st.write("• What is the status of ORD1001?")
    st.write("• What is 125 * 8?")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("tools"):
            st.caption("Tools used: " + ", ".join(message["tools"]))

query = st.chat_input("Ask OmniAssist something...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = httpx.post(
                    f"{API_URL.rstrip('/')}/ask",
                    json={"query": query},
                    timeout=90.0,
                )
                response.raise_for_status()
                data = response.json()
                answer = data["answer"]
                tools_used = data.get("tools_used", [])
                st.markdown(answer)
                if tools_used:
                    st.caption("Tools used: " + ", ".join(tools_used))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "tools": tools_used,
                })
            except httpx.ConnectError:
                st.error("FastAPI is not running. Start it with: uv run uvicorn app.main:app --reload")
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text
                st.error(f"FastAPI returned {exc.response.status_code}: {detail}")
            except Exception as exc:
                st.error("I couldn't process that request right now.")
                with st.expander("Technical details"):
                    st.exception(exc)
