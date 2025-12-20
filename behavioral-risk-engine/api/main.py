from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine.pipeline.run_mvp_pipeline import run_mvp_pipeline
from fastapi import UploadFile, File
import shutil
import os


app = FastAPI(
    title="Behavioral Risk Engine",
    version="0.1.0"
)

# Allow frontend access (React or .NET)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

LAST_UPLOADED_FILE = "data/sample_posts.csv" 

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    global LAST_UPLOADED_FILE
    temp_path = f"data/uploads/temp_{file.filename}"
    
    # Save file
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update state to use this file for subsequent requests
    LAST_UPLOADED_FILE = temp_path
    return run_mvp_pipeline(temp_path)

@app.get("/api/dashboard")
def get_current_data():
    # Uses the newest temp_file if it exists, otherwise defaults to sample
    target_file = LAST_UPLOADED_FILE if os.path.exists(LAST_UPLOADED_FILE) else "data/sample_posts.csv"
    return run_mvp_pipeline(target_file)