"""
agent.py
--------
This is the brain of the project. It:
  1. Loads the vector database we built earlier (chroma_db)
  2. Wraps it as a "retriever tool" so the agent can search policy docs
  3. Combines it with our custom tools (order status, returns, etc.)
  4. Creates an OpenAI-powered agent that decides which tool to use
  5. Adds memory so it remembers earlier messages in the same conversation
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from tools import custom_tools


def build_agent():
    # ---- 1. Load the LLM ----
    # temperature=0 makes answers more consistent/less random - good for
    # a support bot where you don't want creative/inconsistent answers.
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # ---- 2. Load the existing vector database ----
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="ecommerce_policies"
    )
    # k=3 means "return the 3 most relevant chunks" for each search
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # ---- 3. Wrap the retriever as a tool ----
    # This description is IMPORTANT - the LLM reads it to decide when
    # to search policy documents vs. use a different tool.
    retriever_tool = create_retriever_tool(
        retriever,
        name="search_store_policies",
        description=(
            "Search for information about return policy, refund policy, "
            "and shipping policy. Use this for general questions like "
            "'what is your return window' or 'how long do refunds take', "
            "NOT for looking up a specific customer's order."
        )
    )

    # Combine the RAG tool with our custom action tools
    all_tools = [retriever_tool] + custom_tools

    # ---- 4. Build the prompt ----
    # This tells the agent its role and reserves slots for chat history
    # and the "scratchpad" (where the agent's tool-calling steps go).
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a friendly and helpful e-commerce customer support "
            "assistant. Use the available tools to answer questions about "
            "orders, returns, refunds, and shipping policies. "
            "If you don't know something, say so honestly instead of "
            "guessing. Keep answers clear and concise."
        )),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    # ---- 5. Create the agent and its executor ----
    # The "agent" decides WHAT to do next (call a tool or answer).
    # The "AgentExecutor" actually RUNS that loop until it has a final answer.
    agent = create_openai_tools_agent(llm, all_tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,          # prints each step to the console - great for learning/debugging
        handle_parsing_errors=True
    )

    # ---- 6. Add memory (so it remembers earlier turns in the conversation) ----
    # We keep one chat history per "session_id" so multiple users don't mix up.
    session_histories = {}

    def get_session_history(session_id: str):
        if session_id not in session_histories:
            session_histories[session_id] = InMemoryChatMessageHistory()
        return session_histories[session_id]

    agent_with_memory = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return agent_with_memory


# Quick manual test: run "python agent.py" to chat in the terminal
if __name__ == "__main__":
    bot = build_agent()
    session_id = "terminal_test_user"

    print("E-commerce Support Bot (type 'quit' to exit)")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "quit":
            break

        response = bot.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"\nBot: {response['output']}")
