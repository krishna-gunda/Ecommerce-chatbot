# 🛒 E-commerce Support Bot

A friendly AI chatbot that answers customer support questions for an online store — it can explain policies (returns, refunds, shipping) **and** look up real order details, using LangChain + OpenAI.

Built as a beginner-friendly portfolio project to demonstrate **Retrieval-Augmented Generation (RAG)** combined with **tool-calling agents**.

---

## ✨ What this bot can do

| You ask... | It does... |
|---|---|
| "What's your return window for electronics?" | Searches policy documents (RAG) |
| "Where is my order ORD1005?" | Looks up live order status from the database |
| "How long do refunds take?" | Searches policy documents (RAG) |
| "I want to return ORD1010, it's the wrong size" | Initiates a return through a custom tool |

The bot automatically figures out which of these to do — you don't have to tell it. That's the "agent" part.

---

## 🧠 How it works (in plain English)

1. **Policy documents** (return/refund/shipping `.txt` files) get chopped into small chunks and converted into "embeddings" — numeric representations of meaning — and stored in a local vector database called **ChromaDB**.
2. A **mock order database** (SQLite) holds 30 fake orders with realistic statuses like "Shipped" or "Delivered".
3. A **LangChain agent** reads your question, decides whether it needs to search the policy documents or look something up in the order database, calls the right tool, and replies in natural language.
4. Everything runs through a simple **Streamlit** chat window in your browser.

---

## 📁 Project structure

```
ecommerce_support_bot/
├── data/
│   ├── policies/              # Knowledge base: policy documents
│   │   ├── return_policy.txt
│   │   ├── refund_policy.txt
│   │   └── shipping_policy.txt
│   ├── seed_data.py           # Creates the dummy orders database
│   └── orders.db              # Created after you run seed_data.py
├── chroma_db/                 # Created after you run build_vectorstore.py
├── tools.py                   # Order lookup & return tools
├── build_vectorstore.py       # Loads docs → chunks → embeddings
├── agent.py                   # The LangChain agent (brain of the bot)
├── main.py                    # FastAPI backend (optional, for API access)
├── app_streamlit.py           # Chat UI you actually use
├── requirements.txt           # List of packages to install
└── .env.example               # Template for your API key
```

---

## 🚀 Getting started

Follow these steps **in order**. Each one only needs to be done once, except the last step.

### Step 1 — Create a virtual environment

A virtual environment keeps this project's packages separate from everything else on your computer.

```bash
python -m venv venv
```

Activate it:
- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

You'll see `(venv)` appear at the start of your terminal line when it's active.

### Step 2 — Install the required packages

```bash
pip install -r requirements.txt
```

This installs LangChain, OpenAI's SDK, ChromaDB, FastAPI, and Streamlit — everything the project needs.

### Step 3 — Add your OpenAI API key

1. Copy `.env.example` and rename the copy to `.env`
2. Open `.env` and paste your real key:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
   ```
3. Don't have a key? Get one at https://platform.openai.com/api-keys

> ⚠️ Never share your `.env` file or commit it to GitHub — it contains your private key.

### Step 4 — Create the dummy order data

```bash
cd data
python seed_data.py
cd ..
```

This generates 30 fake orders (like `ORD1001`, `ORD1002`...) so you have something to test order lookups with.

### Step 5 — Build the knowledge base

```bash
python build_vectorstore.py
```

This reads the policy documents, splits them into chunks, turns them into embeddings, and saves them into a local `chroma_db` folder. You'll see a test search result print at the end to confirm it worked.

### Step 6 — Test the bot in your terminal (recommended first)

```bash
python agent.py
```

Try asking:
- `What is the return window for electronics?`
- `Where is my order ORD1005?` *(use any order ID printed in Step 4)*
- `I want to return ORD1010, it doesn't fit`

Type `quit` to exit.

### Step 7 — Launch the chat app

```bash
streamlit run app_streamlit.py
```

This opens a proper chat window in your browser at `http://localhost:8501`.

---

## 🔁 Quick reference — every time you want to use the bot again

You don't need to repeat Steps 1–5 every time. Just:

```bash
source venv/bin/activate        # or venv\Scripts\activate on Windows
streamlit run app_streamlit.py
```

---

## 🛠️ Troubleshooting

**"ImportError: cannot import name 'create_openai_tools_agent' from 'langchain.agents'"**
This means a newer, incompatible version of LangChain got installed. Fix it by reinstalling the exact versions this project needs:
```bash
pip uninstall langchain langchain-openai langchain-community langchain-chroma langchain-text-splitters -y
pip install langchain==0.3.7 langchain-openai==0.2.9 langchain-community==0.3.7 langchain-chroma==0.1.4 langchain-text-splitters==0.3.2
```

**"No module named 'langchain'" (or similar)**
Your virtual environment probably isn't activated. Run the activate command from Step 1 again — you should see `(venv)` in your terminal.

**"Invalid API key" or authentication errors**
Double-check your `.env` file has the correct key with no extra spaces or quotes around it.

**The bot says it can't find an order**
Make sure you ran `python seed_data.py` (Step 4), and that you're using an order ID it actually printed (e.g. `ORD1001`–`ORD1030`).

**Streamlit opens but the page is blank or errors immediately**
Check the terminal where you ran `streamlit run` — the real error message shows up there, not just in the browser.

---

## 💡 Why dummy data instead of real order tracking?

Real courier tracking (Delhivery, BlueDart, FedEx, etc.) requires paid business accounts and contracts, so this project simulates order data instead. This is completely standard for a learning/portfolio project. The lookup code is written the same way it would be for a real database — so swapping in a real courier API later only means changing what's inside `tools.py`, not the agent's logic.

---

## 🌱 Ideas for improving this project further

- Add a **reranker** (e.g. Cohere rerank) to improve search precision
- Add **RAGAS evaluation** to measure how faithful/accurate the bot's answers are
- Add a background job that randomly advances order statuses over time, to simulate real-time tracking
- Swap SQLite for **PostgreSQL** for a more production-like setup
- Deploy the backend to **Render** and the frontend to **Streamlit Community Cloud**
- Add source citations in the bot's replies (show which policy doc an answer came from)

---

## 📚 Tech stack

- **Python** 3.11+
- **LangChain** — agent framework + RAG pipeline
- **OpenAI API** — `gpt-4o-mini` for chat, `text-embedding-3-small` for embeddings
- **ChromaDB** — local vector database
- **SQLite** — mock order database
- **FastAPI** — optional backend API
- **Streamlit** — chat interface
