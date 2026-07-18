"""
app_streamlit.py
-----------------
A simple chat interface for the support bot, built with Streamlit.

Run it with:
    streamlit run app_streamlit.py

Note: this calls the agent directly (not through FastAPI) to keep things
simple for a first version. Once your FastAPI backend is deployed, you can
switch this to call it over HTTP with the `requests` library instead.
"""

import streamlit as st
from agent import build_agent

st.set_page_config(page_title="E-commerce Support Bot", page_icon="🛒")
st.title("E-commerce Support Bot")
st.caption("Ask me about your order status, returns, refunds, or shipping policies.")

# Build the agent once and keep it in Streamlit's session state
# (otherwise it would rebuild on every single interaction, which is slow)
if "bot" not in st.session_state:
    st.session_state.bot = build_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input box
user_input = st.chat_input("Type your question here...")

if user_input:
    # Show the user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Get the bot's response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.bot.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": "streamlit_user"}}
            )
            reply = result["output"]
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
