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

@app.get("/")
def ping():
    return {"message": "Welcome aboard!"}

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/upload")
async def endpoint(uploaded_file: UploadFile):
    return { "code": 200, "message": "success", "data": audio_controller.upload(uploaded_file) }