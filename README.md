# E-commerce Support Bot (LangChain + OpenAI)

A beginner-friendly agentic RAG project: an e-commerce customer support
chatbot that can answer policy questions (using RAG over documents) AND
look up real order details (using tool-calling over a mock database).

## What this project demonstrates

- Document loading, chunking, and embedding (RAG pipeline)
- Vector search with ChromaDB
- LangChain agents with tool-calling (no LangGraph needed)
- Conversation memory across turns
- A working FastAPI backend + Streamlit frontend

## Project structure

```
ecommerce_support_bot/
├── data/
│   ├── policies/              # policy documents (the RAG knowledge base)
│   │   ├── return_policy.txt
│   │   ├── refund_policy.txt
│   │   └── shipping_policy.txt
│   ├── seed_data.py            # creates the dummy orders.db
│   └── orders.db                # created after running seed_data.py
├── chroma_db/                    # created after running build_vectorstore.py
├── tools.py                      # custom tools (order status, returns, etc.)
├── build_vectorstore.py          # loads docs -> chunks -> embeddings -> ChromaDB
├── agent.py                      # the LangChain agent (RAG tool + custom tools)
├── main.py                       # FastAPI backend
├── app_streamlit.py              # Streamlit chat frontend
├── requirements.txt
└── .env.example
```

## Setup steps (run these in order)

### 1. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your OpenAI API key

Copy `.env.example` to `.env` and paste your real key in:

```bash
cp .env.example .env
```

Then edit `.env` so it looks like:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
```

Get a key from https://platform.openai.com/api-keys if you don't have one.

### 3. Create the dummy orders database

```bash
cd data
python seed_data.py
cd ..
```

This creates `data/orders.db` with 30 realistic fake orders.

### 4. Build the vector database (chunking + embeddings)

```bash
python build_vectorstore.py
```

This reads the 3 policy `.txt` files, splits them into ~500-character
chunks, turns each chunk into an embedding using OpenAI, and saves
everything into a local `chroma_db/` folder. You'll see a test search
result printed at the end to confirm it worked.

### 5. Test the agent in your terminal (optional but recommended)

```bash
python agent.py
```

Try asking things like:
- "What is the return window for electronics?"
- "Where is my order ORD1005?" (use any order ID printed by seed_data.py)
- "How long do refunds take?"
- "I want to return ORD1010, it's the wrong size"

Type `quit` to exit.

### 6. Run the FastAPI backend

```bash
uvicorn main:app --reload
```

Visit http://127.0.0.1:8000/docs to test the `/chat` endpoint directly.

### 7. Run the Streamlit frontend (in a new terminal)

```bash
streamlit run app_streamlit.py
```

This opens a chat UI in your browser.

## How it decides what to do

The agent looks at each message and picks the right tool automatically:

| Question type | Tool used |
|---|---|
| "What's your return policy for clothes?" | `search_store_policies` (RAG) |
| "Where is my order ORD1003?" | `get_order_status` |
| "What did I order in ORD1003?" | `get_order_details` |
| "I want to return ORD1003" | `initiate_return` |

You don't write this routing logic yourself - the LLM reads each tool's
docstring and decides which one fits the question.

## Notes on the dummy data

Real courier tracking APIs (Delhivery, BlueDart, etc.) require paid
business accounts, so this project uses a simulated SQLite database
instead. The order lookup code queries this database exactly the way it
would query a real one - so swapping in a real courier API later only
means replacing what's inside `tools.py`, not changing the agent's logic.

## Possible next improvements

- Add a reranker (e.g. Cohere rerank) after retrieval for better precision
- Add RAGAS evaluation to measure answer faithfulness
- Add a background job (APScheduler) that randomly advances order
  statuses over time, to simulate live tracking
- Swap SQLite for PostgreSQL
- Deploy backend to Render and frontend to Streamlit Cloud
