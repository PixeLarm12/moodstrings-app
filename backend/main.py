import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from src.controllers import AudioController as audio_controller
from src.controllers import AdminController as admin_controller
from src.utils import StringUtil
from music21 import chord as m21Chord, harmony as m21Harmony
from src.services.AITrainingService import AITrainingService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-file")
async def transcribe(
    uploaded_file: UploadFile = File(...),
    is_recorded: int = Form(...)
):
    return audio_controller.transcribe(uploaded_file, is_recorded)

@app.post("/get-progression-info")
async def get_progression_info(
    chordProgression: str = Form(...),
    tempo: int = Form(...),
    uploaded_file: UploadFile = File(...)
):  
    return audio_controller.progression_info(chordProgression, tempo, uploaded_file)

@app.post("/download-midi")
async def download_midi(uploaded_file: UploadFile):
    return await audio_controller.get_midi_to_download(uploaded_file)

@app.post("/download-sheet")
async def download_sheet(uploaded_file: UploadFile):
    return await audio_controller.get_musical_sheet_to_download(uploaded_file)

@app.get("/split-dataset")
def split_dataset():
    service = AITrainingService();
    service.split_raw_dataset()

    return {
        "message": "spliting dataset"
    }

@app.get("/train-rf")
def train_rf():
    service = AITrainingService();
    service.train_model()
    
    return {
        "message": "training random forest"
    }

@app.get("/chunk-dataset")
def chunk_dataset():
    service = AITrainingService("chunk");
    service.chunk_dataset_based_on_forteclasses_average()
    
    return {
        "message": "chunking random forest"
    }

@app.get("/split-chunk-dataset")
def split_chunk_dataset():
    service = AITrainingService();
    service.split_chunk_dataset()
    
    return {
        "message": "spliting chunk dataset"
    }

@app.get("/train-rf-chunked")
def train_rf_chunked():
    service = AITrainingService();
    service.train_chunk_model()
    
    return {
        "message": "training chunked random forest"
    }