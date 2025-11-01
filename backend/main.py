import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from src.controllers import AudioController as audio_controller
from src.controllers import AdminController as admin_controller
from src.utils import StringUtil
from music21 import chord as m21Chord, harmony as m21Harmony

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
    noteProgression: str = Form(...),
    tempo: int = Form(...),
    uploaded_file: UploadFile = File(...)
):  
    return audio_controller.progression_info(chordProgression, noteProgression, tempo, uploaded_file)

@app.post("/download-midi")
async def download_midi(uploaded_file: UploadFile):
    return await audio_controller.get_midi_to_download(uploaded_file)

@app.post("/download-sheet")
async def download_sheet(uploaded_file: UploadFile):
    return await audio_controller.get_musical_sheet_to_download(uploaded_file)

@app.post("/test")
async def test(progression: str = Form(...)):
    # chords_list = []
    # chords_list.append("C-major triad")
    # chords_list.append("Major Third above C")
    # chords_list.append("D-major triad")
    # chords_list.append("E-major triad")
    # chords_list.append("F-major triad")
    # chords_list.append("G-major triad")
    # chords_list.append("Perfect Fourth above D")
    # chords_list.append("Perfect Fourth above E")
    # chords_list.append("A-major triad")
    # chords_list.append("enharmonic equivalent to major triad above Eb")
    # chords_list.append("enharmonic equivalent to major triad above Eb")

    # C-Cm-Bb-F#-F#m-C9-A7M-Em7
    chords_list = [
        ch.strip().replace('"', '').replace('b', '♭').replace('#', '♯') #unicode fix
        for ch in progression.split("-")
    ]

    for chord in chords_list:
        chord = m21Harmony.ChordSymbol("Bdim")

        StringUtil.define_chord_name(chord.pitchedCommonName)

    return 1

    # return ;