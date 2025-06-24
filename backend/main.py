from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.controllers import AudioController as audio_controller

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def endpoint(uploaded_file: UploadFile):
    return { "code": 200, "message": "success", "data": audio_controller.upload(uploaded_file) }