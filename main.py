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
    expose_headers=["Access-Control-Allow-Origin"]
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

class Consent(BaseModel):
    session_id: str
    participant_name: str
    consent_given: bool

class PollResponse(BaseModel):
    session_id: str
    participant_name: str
    poll_question: str
    poll_answer: str

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
        "participant_name": feedback.participant_id,
        "message": feedback.message
    }
    result = supabase.table("raw_feedbacks").insert(data).execute()
    return {"status": "success", "data": result}

# API endpoint to save consent (only when participant votes yes)
@app.post("/consents")
async def save_consent(consent: Consent):
    data = {
        "session_id": consent.session_id,
        "participant_name": consent.participant_name,
        "consent_given": consent.consent_given
    }
    result = supabase.table("consents").insert(data).execute()
    return {"status": "success", "data": result}

# API endpoint to save poll response
@app.post("/poll-responses")
async def save_poll_response(response: PollResponse):
    data = {
        "session_id": response.session_id,
        "participant_name": response.participant_name,
        "poll_question": response.poll_question,
        "poll_answer": response.poll_answer
    }
    result = supabase.table("poll_responses").insert(data).execute()
    return {"status": "success", "data": result}

# API endpoint to analyze feedback with AI pipeline
@app.post("/analyze")
async def analyze_feedback(feedback: Feedback):
    print(f"[FA:AI] Received message for analysis: {feedback.message[:50]}...")
    
    try:
        # Import AI pipeline
        import sys
        import os
        
        # Add ai-pipeline to path - use absolute path from project root
        project_root = os.path.dirname(os.path.abspath(__file__))
        ai_pipeline_path = os.path.join(project_root, 'ai-pipeline')
        
        if ai_pipeline_path not in sys.path:
            sys.path.insert(0, ai_pipeline_path)
        
        # Change to ai-pipeline directory so imports work correctly
        original_cwd = os.getcwd()
        try:
            os.chdir(ai_pipeline_path)
            from pipelines.run_full_pipeline import run_pipeline
        finally:
            os.chdir(original_cwd)
        
        print("[FA:AI] Running AI pipeline...")
        
        # Run pipeline
        results = run_pipeline([feedback.message], return_only_pedagogical=False)
        
        if not results:
            print("[FA:AI] No results from pipeline")
            return {"status": "error", "message": "No results from pipeline"}
        
        result = results[0]
        
        print(f"[FA:AI] Classification result: {'pedagogical' if result.is_pedagogical else 'nonsensical'}")
        print(f"[FA:AI] Problem detected: {result.problem}")
        print(f"[FA:AI] Strategy recommended: {result.primary_strategy}")
        print(f"[FA:AI] Topic: {result.topic_label}")
        
        # Save to Supabase tables - skip if tables don't exist
        # Just return the results without saving to database for now
        print("[FA:AI] Analysis complete - returning results")
        
        return {
            "original": result.original_text,
            "is_pedagogical": result.is_pedagogical,
            "problem": result.problem,
            "strategy": result.primary_strategy,
            "topic": result.topic_label,
            "errors": result.stage_errors
        }
        
    except Exception as e:
        print(f"[FA:AI] Error during analysis: {str(e)}")
        import traceback
        print(f"[FA:AI] Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": str(e),
            "original": feedback.message,
            "is_pedagogical": False,
            "problem": None,
            "strategy": None,
            "topic": None
        }

# API endpoint to delete all data for a session
@app.delete("/sessions/{session_id}")
async def delete_session_data(session_id: str):
    try:
        # Delete in the correct order following the foreign key relationships
        # First, delete from tables that have direct session_id reference
        
        # For the feedback processing chain, we need to delete in cascade
        # Get all raw_feedbacks for this session first (these have session_id)
        raw_feedbacks_result = supabase.table("raw_feedbacks").select("id").eq("session_id", session_id).execute()
        raw_feedback_ids = [item["id"] for item in raw_feedbacks_result.data] if raw_feedbacks_result.data else []
        
        if raw_feedback_ids:
            # Delete all related records in the processing chain
            # teaching_recommendations <- identified_problems <- categorized_feedbacks <- preprocessed_feedbacks <- raw_feedbacks
            # We need to delete from the end of the chain backwards
            
            # Get preprocessed feedback IDs linked to raw feedbacks
            preprocessed_result = supabase.table("preprocessed_feedbacks").select("id").in_("raw_feedback_id", raw_feedback_ids).execute()
            preprocessed_ids = [item["id"] for item in preprocessed_result.data] if preprocessed_result.data else []
            
            # Get categorized feedback IDs linked to preprocessed feedbacks
            categorized_result = supabase.table("categorized_feedbacks").select("id").in_("preprocessed_feedback_id", preprocessed_ids).execute()
            categorized_ids = [item["id"] for item in categorized_result.data] if categorized_result.data else []
            
            # Get theme IDs linked to preprocessed feedbacks
            theme_result = supabase.table("feedback_themes").select("id").in_("preprocessed_feedback_id", preprocessed_ids).execute()
            theme_ids = [item["id"] for item in theme_result.data] if theme_result.data else []
            
            # Get problem IDs linked to categorized feedbacks
            problem_result = supabase.table("identified_problems").select("id").in_("categorized_feedback_id", categorized_ids).execute()
            problem_ids = [item["id"] for item in problem_result.data] if problem_result.data else []
            
            # Delete in reverse order
            if problem_ids:
                supabase.table("teaching_recommendations").delete().in_("problem_id", problem_ids).execute()
                supabase.table("identified_problems").delete().in_("id", problem_ids).execute()
            if theme_ids:
                supabase.table("feedback_themes").delete().in_("id", theme_ids).execute()
            if categorized_ids:
                supabase.table("categorized_feedbacks").delete().in_("id", categorized_ids).execute()
            if preprocessed_ids:
                supabase.table("preprocessed_feedbacks").delete().in_("id", preprocessed_ids).execute()
            
            # Finally delete the raw feedbacks
            supabase.table("raw_feedbacks").delete().in_("id", raw_feedback_ids).execute()
        
        # Delete other session-related data
        supabase.table("poll_responses").delete().eq("session_id", session_id).execute()
        supabase.table("consents").delete().eq("session_id", session_id).execute()
        
        # Finally, delete the session itself
        supabase.table("sessions").delete().eq("id", session_id).execute()
        
        print(f"Deleted session {session_id} and all related data successfully")
        return {"status": "success", "deleted_records": True}
    except Exception as e:
        print(f"Error deleting session {session_id}: {str(e)}")
        return {"status": "error", "message": str(e)}

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
