from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os

# Your Supabase credentials
SUPABASE_URL = "https://iapkqaaiifkazxdyftpz.supabase.co"
SUPABASE_KEY = "sb_publishable_G49_FQHkfrEtQfQ6cT5b5g_L5ErfkBF"

app = FastAPI()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Data models
class Feedback(BaseModel):
    session_id: str
    participant_id: str
    message: str

# API endpoint to receive feedback
@app.post("/feedback")
async def receive_feedback(feedback: Feedback):
    data = {
        "session_id": feedback.session_id,
        "participant_id": feedback.participant_id,
        "message": feedback.message
    }
    result = supabase.table("raw_feedbacks").insert(data).execute()
    return {"status": "success", "data": result}

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
