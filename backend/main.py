from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.controllers import AudioController as audio_controller
from src.controllers import AdminController as admin_controller

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-file")
async def transcribe(uploaded_file: UploadFile):
    return audio_controller.test_audio(uploaded_file)

# @app.get("/create-dataset")
# def create_dataset():
#     return { "code": 200, "message": "success", "data": admin_controller.create_dataset() }

# @app.get("/normalize-dataset")
# def normalize_dataset():
#     return { "code": 200, "message": "success", "data": admin_controller.normalize_dataset() }