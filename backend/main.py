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

@app.post("/upload")
async def endpoint(uploaded_file: UploadFile):
    return { "code": 200, "message": "success", "data": audio_controller.upload(uploaded_file) }

@app.post("/testmp3")
async def transcribe(uploaded_file: UploadFile):
    return await audio_controller.test_mp3(uploaded_file)

# @app.get("/create-dataset")
# def create_dataset():
#     return { "code": 200, "message": "success", "data": admin_controller.create_dataset() }

# @app.get("/normalize-dataset")
# def normalize_dataset():
#     return { "code": 200, "message": "success", "data": admin_controller.normalize_dataset() }