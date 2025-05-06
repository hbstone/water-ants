from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

from app.models.analyzer import analyze_drawing
from app.services.task_selector import get_next_task
from app.services.feedback import generate_feedback

app = FastAPI()

# CORS (allow frontend to access this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://water-ants.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Data Models ----------

class Submission(BaseModel):
    user_id: str
    task_id: str
    strokes: List[dict]  # Optional: if using stroke input as JSON
    # image will come separately as UploadFile

class FeedbackResponse(BaseModel):
    feedback: str
    score: float
    next_task_id: str
    next_prompt_url: str

# ---------- Routes ----------

@app.post("/submit", response_model=FeedbackResponse)
async def submit_drawing(
    user_id: str = Form(...),
    task_id: str = Form(...),
    image: UploadFile = File(...),
    strokes: str = Form(None)  # Optional, JSON stringified
):
    # Analyze the user's drawing
    analysis_result = analyze_drawing(image, strokes)

    # Generate insights and constructive feedback
    feedback = generate_feedback(analysis_result)

    # Choose appropriate next drawing task based on the user's updated drawing profile
    next_task = get_next_task(user_id, analysis_result)

    return FeedbackResponse(
        feedback=feedback["text"],
        score=feedback["score"],
        next_task_id=next_task["id"],
        next_prompt_url=next_task["image_url"]
    )

@app.get("/task")
def get_prompt():
    # For demo: return a fixed prompt
    return {
        "task_id": "cube_001",
        "image_url": "/static/prompts/cube_001.png",
        "instructions": "Draw this cube as accurately as possible."
    }

# ---------- Entry Point ----------

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
