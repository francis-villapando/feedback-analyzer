from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from datetime import datetime
import os

# Your Supabase credentials
SUPABASE_URL = "https://iapkqaaiifkazxdyftpz.supabase.co"
SUPABASE_KEY = "sb_publishable_G49_FQHkfrEtQfQ6cT5b5g_L5ErfkBF"

app = FastAPI()

# Add CORS middleware to allow Chrome extension requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Data models
class SessionCreate(BaseModel):
    meet_link: str
    course_id: str
    topic_id: str

class Feedback(BaseModel):
    session_id: str
    participant_id: str
    message: str

# API endpoint to get all courses
@app.get("/courses")
async def get_courses():
    result = supabase.table("courses").select("id, name, description").execute()
    return result.data

# API endpoint to get topics for a course
@app.get("/courses/{course_id}/topics")
async def get_course_topics(course_id: str):
    result = supabase.table("topics").select("id, name, description").eq("course_id", course_id).execute()
    return result.data

# API endpoint to create a new session
@app.post("/sessions")
async def create_session(session: SessionCreate):
    data = {
        "meet_link": session.meet_link,
        "course_id": session.course_id,
        "topic_id": session.topic_id
    }
    result = supabase.table("sessions").insert(data).execute()
    return {"status": "success", "session_id": result.data[0]["id"]}

# API endpoint to end a session
@app.patch("/sessions/{session_id}/end")
async def end_session(session_id: str):
    result = supabase.table("sessions").update({"ended_at": datetime.utcnow().isoformat()}).eq("id", session_id).execute()
    return {"status": "success"}

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
