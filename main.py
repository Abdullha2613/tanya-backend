import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Tanya AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
APP_TOKEN = os.environ.get("APP_TOKEN", "dev-token")

SYSTEM_PROMPT = """You are Tanya, a friendly voice assistant on the user's Android phone.
Rules:
- Reply in the same language the user speaks (Bangla or English).
- Keep replies SHORT - max 2 sentences.
- Be warm and helpful.
"""

class ChatRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def health():
    return {"status": "ok", "service": "Tanya AI"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, x_app_token: str = Header(default="")):
    if x_app_token != APP_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.text},
            ],
            temperature=0.7,
            max_tokens=200,
        )
        reply = resp.choices[0].message.content or "Sorry, no reply."
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
