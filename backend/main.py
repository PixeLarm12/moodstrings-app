import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from src.controllers import AudioController as audio_controller
from src.controllers import AdminController as admin_controller
from src.utils import StringUtil
from music21 import chord as m21Chord, harmony as m21Harmony
from src.services.AITrainingService import AITrainingService
from src.services.RandomForestService import RandomForestService
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


"""
Routes to train the basic random forest model
"""
@app.get("/train-rf")
def train_rf():
    service = AITrainingService();
    service.train_model()
    
    return {
        "message": "training random forest"
    }


"""
Routes to create, split and train the chunked random forest dataset and model
"""
@app.get("/create-chunk-dataset")
def create_chunk_dataset():
    service = AITrainingService();
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


"""
Routes to create, split and train the chunked random forest dataset and model with N-grams and LDA
"""
@app.get("/create-ngrams-dataset")
def create_ngrams_dataset():
    service = AITrainingService();
    service.build_ngrams_dataset()
    
    return {
        "message": "building ngrams dataset"
    }

@app.get("/split-ngrams-dataset")
def split_ngrams_dataset():
    service = AITrainingService();
    service.split_ngrams_dataset()
    
    return {
        "message": "spliting ngrams dataset"
    }

@app.get("/train-rf-ngrams")
def train_rf_ngrams():
    service = AITrainingService();
    service.train_ngrams_model()
    
    return {
        "message": "training ngrams random forest"
    }

"""
Routes to create, split and train the basic random forest dataset and model with N-grams and LDA
"""
@app.get("/create-full-ngrams-dataset")
def create_full_ngrams_dataset():
    service = AITrainingService();
    service.build_full_ngrams_dataset()
    
    return {
        "message": "building full ngrams dataset"
    }

@app.get("/split-full-ngrams-dataset")
def split_full_ngrams_dataset():
    service = AITrainingService();
    service.split_full_ngrams_dataset()
    
    return {
        "message": "spliting full ngrams dataset"
    }

@app.get("/train-rf-full-ngrams")
def train_rf_full_ngrams():
    service = AITrainingService();
    service.train_full_ngrams_model()
    
    return {
        "message": "training full ngrams random forest"
    }

@app.get("/find-evaluation")
def find_evaluation():
    service = RandomForestService();
    evaluation = service.evaluate_balanced_ngrams()
    # service.predict("3-11B,3-11B,3-11B,3-11B,3-11B,3-11B,3-11B,3-11", "major")
    
    return {
        "evaluation_result": evaluation
    }

@app.get("/create-dataset-five-classes")
def create_five_classes_dataset():
    service = XMIDIService();
    dataset_path = service.build_dataset(overwrite=True)
    
    return {
        "dataset_raw_path": dataset_path
    }

"""
Routes to create, split and train the balanced chunked random forest dataset and model
"""
@app.get("/create-balanced-chunk-dataset")
def create_balanced_chunk_dataset():
    service = AITrainingService();
    service.create_balanced_chunk_dataset()
    
    return {
        "message": "building chunk dataset"
    }

@app.get("/split-balanced-chunk-dataset")
def split_balanced_chunk_dataset():
    service = AITrainingService();
    service.split_balanced_chunk_dataset()
    
    return {
        "message": "spliting balanced chunk dataset"
    }

@app.get("/train-rf-balanced")
def train_rf_balanced():
    service = AITrainingService();
    service.train_balanced_chunk_model()

    return {
        "message": "training balanced chunk random forest"
    }


"""
Routes to create, split and train the balanced ngrams random forest dataset and model
"""
@app.get("/create-balanced-ngrams-dataset")
def create_balanced_ngrams_dataset():
    service = AITrainingService();
    service.create_balanced_dataset_ngrams_lda()
    
    return {
        "message": "building balanced ngrams dataset"
    }

@app.get("/split-balanced-ngrams-dataset")
def split_balanced_ngrams_dataset():
    service = AITrainingService();
    service.split_balanced_dataset_ngrams_lda()
    
    return {
        "message": "spliting balanced ngrams dataset"
    }

@app.get("/train-rf-balanced-ngrams")
def train_rf_balanced_ngrams():
    service = AITrainingService();
    service.train_model_ngrams_lda_balanced()

    return {
        "message": "training balanced ngrams random forest"
    }

@app.get("/create-50-chunk")
def create_50_chunk():
    service = AITrainingService();
    service.chunk_50_dataset()

    return {
        "message": "created chunked 50 random forest"
    }

@app.get("/split-50-chunk")
def split_50_chunk():
    service = AITrainingService();
    service.split_chunked_50_dataset()

    return {
        "message": "split chunked 50 random forest"
    }

@app.get("/train-50-chunk")
def train_50_chunk():
    service = AITrainingService();
    service.train_chunked_50_model()

    return {
        "message": "train chunked 50 random forest"
    }