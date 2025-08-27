# SetSculptor_AI_Backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv, io, json

app = FastAPI(title="SetSculptor API")

# CORS (leave * for now; later restrict to your domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------
class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    reply: str

class AnalyzeOut(BaseModel):
    summary: dict

# ---------- Health ----------
@app.get("/", tags=["health"])
def root():
    return {"message": "SetSculptor Backend Running"}

# ---------- Simple chat endpoint ----------
@app.post("/chat", response_model=ChatOut, tags=["chat"])
def chat(payload: ChatIn):
    msg = payload.message.lower()

    if ("push" in msg and "chest" in msg) or ("triceps" in msg):
        plan = [
            {"exercise": "Bench Press", "sets": 4, "reps": "6–8"},
            {"exercise": "Incline DB Press", "sets": 3, "reps": "8–10"},
            {"exercise": "Cable Flyes", "sets": 3, "reps": "12–15"},
            {"exercise": "Overhead Rope Extensions", "sets": 3, "reps": "10–12"},
            {"exercise": "Dips (assist if needed)", "sets": 3, "reps": "AMRAP"},
        ]
        return ChatOut(reply=json.dumps(plan))
    else:
        return ChatOut(reply="Got it. Tell me what body part or goal you want and I’ll build a plan.")

# ---------- File analyze endpoint ----------
@app.post("/analyze", response_model=AnalyzeOut, tags=["analyze"])
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    name = file.filename or "upload"

    try:
        if name.lower().endswith(".csv"):
            text = content.decode("utf-8", errors="ignore")
            rows = list(csv.reader(io.StringIO(text)))
            headers = rows[0] if rows else []
            summary = {
                "type": "csv",
                "filename": name,
                "rows": len(rows) - 1 if len(rows) > 1 else 0,
                "columns": len(headers),
                "headers": headers,
            }
        elif name.lower().endswith(".json"):
            data = json.loads(content.decode("utf-8", errors="ignore"))
            keys = list(data.keys()) if isinstance(data, dict) else []
            summary = {
                "type": "json",
                "filename": name,
                "top_level_keys": keys,
            }
        elif name.lower().endswith((".txt", ".md", ".log")):
            text = content.decode("utf-8", errors="ignore")
            summary = {
                "type": "text",
                "filename": name,
                "characters": len(text),
                "lines": len(text.splitlines()),
            }
        else:
            summary = {"type": "binary", "filename": name, "bytes": len(content)}

        return AnalyzeOut(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not analyze file: {e}")
