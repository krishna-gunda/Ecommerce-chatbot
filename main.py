"""
main.py
-------
This is the FastAPI backend. It exposes a single /chat endpoint that the
Streamlit frontend (or anything else) can call.

Run it with:
    uvicorn main:app --reload

Then visit http://127.0.0.1:8000/docs to test it directly in the browser.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from agent import build_agent

app = FastAPI(title="E-commerce Support Bot API")

# Build the agent once when the server starts (not on every request -
# that would be slow and wasteful).
bot = build_agent()


# This defines what the incoming request JSON should look like:
# { "message": "...", "session_id": "..." }
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_user"   # lets different users have separate memory


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def root():
    return {"status": "E-commerce Support Bot API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = bot.invoke(
        {"input": request.message},
        config={"configurable": {"session_id": request.session_id}}
    )
    return ChatResponse(reply=result["output"])
