import os
import re
import pandas as pd
import pretty_midi
from music21 import chord, pitch
from tqdm import tqdm

INSTRUMENTS_TARGET = {
    24: 'guitar',             # Nylon Acoustic Guitar
    25: 'guitar_steel',       # Steel Acoustic Guitar
    26: 'jazz_guitar',
    27: 'clean_guitar',
    28: 'muted_guitar',
    29: 'overdrive_guitar',
    30: 'distortion_guitar',
    31: 'guitar_harmonics'
}

def notes_to_chord_name(pitches: list[int]) -> str:
    if not pitches or len(pitches) < 2:
        return ""  
    try:
        p_notes = [pitch.Pitch(midi=p) for p in pitches]
        c = chord.Chord(p_notes)
        return c.figure
    except Exception:
        return '+'.join([pretty_midi.note_number_to_name(p) for p in pitches])

def extract_chord_sequence(instrument: pretty_midi.Instrument):
    chord_sequence = []
    notes_sorted = sorted(instrument.notes, key=lambda x: x.start)

    i = 0
    while i < len(notes_sorted):
        start_time = notes_sorted[i].start
        chord = [notes_sorted[i].pitch]
        j = i + 1
        while j < len(notes_sorted) and abs(notes_sorted[j].start - start_time) < 0.05:
            chord.append(notes_sorted[j].pitch)
            j += 1
        chord = sorted(chord)
        chord_name = notes_to_chord_name(chord)
        if chord_name and chord_name not in chord_sequence:
            chord_sequence.append(chord_name)
        i = j

    return chord_sequence

def process_midi_file(file_path):
    filename = os.path.basename(file_path)
    match = re.match(r'XMIDI_(\w+)_(\w+)_([a-zA-Z0-9]{8})\.midi', filename)
    if not match:
        return []

    emotion, genre, file_id = match.groups()
    try:
        midi_data = pretty_midi.PrettyMIDI(file_path)
    except Exception as e:
        print(f"Erro ao processar {filename}: {e}")
        return []

    rows = []
    for instrument in midi_data.instruments:
        if instrument.program in INSTRUMENTS_TARGET and not instrument.is_drum:
            progression = extract_chord_sequence(instrument)
            if progression:
                rows.append({
                    'progression': ' - '.join(progression),
                    'instrument': INSTRUMENTS_TARGET[instrument.program],
                    'emotion': emotion,
                    'genre': genre,
                    'file_ID': file_id
                })
    return rows

midi_dir = '/content/drive/MyDrive/UNESP/TCC/Datasets/dataset_test/raw'
output_csv = '/content/drive/MyDrive/UNESP/TCC/Datasets/dataset_test/final/midi_chord_progressions.csv'

all_data = []
for file in tqdm(os.listdir(midi_dir)):
    if file.endswith('.mid') or file.endswith('.midi'):
        file_path = os.path.join(midi_dir, file)
        rows = process_midi_file(file_path)
        all_data.extend(rows)

df = pd.DataFrame(all_data)
df.to_csv(output_csv, index=False)
print(f"\Saved in: {output_csv}")
