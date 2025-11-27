import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from src.controllers import AudioController as audio_controller
from src.services.ModelTrainingService import ModelTrainingService
from src.services.RandomForestService import RandomForestService
from src.services.RFTrainingService import RFTrainingService
from src.services.XMIDIService import XMIDIService

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

# @app.post("/download-midi")
# async def download_midi(uploaded_file: UploadFile):
#     return await audio_controller.get_midi_to_download(uploaded_file)

# @app.post("/download-sheet")
# async def download_sheet(uploaded_file: UploadFile):
#     return await audio_controller.get_musical_sheet_to_download(uploaded_file)

@app.get("/test-evaluation")
def test_evaluation():
    service = RandomForestService();
    full = service.evaluate_model_balanced()
    
    return {
        "full": full,
    }

# @app.get("/build-chunked-dataset")
# def build_chunked_dataset():
#     service = ModelTrainingService();
#     service.build_chunked_dataset()
    
#     return { "message": "built chunk dataset" }

# @app.get("/balance-chunked-dataset")
# def balance_chunked_dataset():
#     service = ModelTrainingService();
#     service.build_balanced_chunked_dataset()
    
#     return { "message": "built balanced dataset" }

# @app.get("/balance-chunked-dataset-traintest")
# def balance_chunked_dataset_traintest():
#     service = ModelTrainingService();
#     service.build_balanced_chunked_dataset_traintest()
    
#     return { "message": "built balanced dataset" }

# @app.get("/split-dataset")
# def split_dataset():
#     service = ModelTrainingService();
#     service.split_balanced_dataset()
    
#     return {
#         "message": "splitted balanced dataset"
#     }

# @app.get("/train-balanced")
# def train_balanced():
#     service = ModelTrainingService();
#     service.train_balanced_dataset()

#     return {
#         "message": "trained balanced random forest"
#     }


# @app.get("/build-full-dataset")
# def build_full_dataset():
#     service = RFTrainingService();
#     service.build_full_dataset()
    
#     return { "message": "built full dataset" }

# @app.get("/split-full_dataset")
# def split_full_dataset():
#     service = RFTrainingService();
#     service.split_full_dataset()
    
#     return {
#         "message": "splitted full dataset"
#     }

# @app.get("/train-full-dataset")
# def train_full_dataset():
#     service = RFTrainingService();
#     service.train_full_dataset()

#     return {
#         "message": "trained full random forest"
#     }