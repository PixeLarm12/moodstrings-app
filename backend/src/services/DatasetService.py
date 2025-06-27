import os
import pandas as pd
import pretty_midi
from pathlib import Path
from io import BytesIO
from tqdm import tqdm

class DatasetService:
    def __init__(self, midi_folder: str, output_path: str):
        self.midi_folder = Path(midi_folder)
        self.output_path = Path(output_path)
        self.general_midi_guitar_names = {
            24: "Acoustic Guitar (nylon)",
            25: "Acoustic Guitar (steel)",
            26: "Electric Guitar (jazz)",
            27: "Electric Guitar (clean)",
            28: "Electric Guitar (muted)",
            29: "Overdriven Guitar",
            30: "Distortion Guitar",
            31: "Guitar Harmonics"
        }

    def process(self):
        all_data = []

        for file_name in tqdm(os.listdir(self.midi_folder), desc="Processing MIDI files"):
            if not (file_name.endswith(".mid") or file_name.endswith(".midi")):
                continue

            full_path = self.midi_folder / file_name

            try:
                with open(full_path, "rb") as f:
                    midi_data = pretty_midi.PrettyMIDI(BytesIO(f.read()))
                    extracted = self._extract_chords_by_guitar_type(midi_data)

                    for item in extracted:
                        all_data.append({
                            "file": file_name,
                            "program": item["program"],
                            "instrument": item["title"],
                            "chords": ' - '.join(['+'.join(c) for c in item["chords"]])
                        })

            except Exception as e:
                print(f"Error to process: {file_name}: {e}")

        if all_data:
            df = pd.DataFrame(all_data)
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.output_path, index=False)
            print(f"Dataset saved on: {self.output_path}")
        else:
            print("Empty data extracted!.")

    def _extract_chords_by_guitar_type(self, midi_data: pretty_midi.PrettyMIDI, chord_threshold=3):
        result = []

        for instrument in midi_data.instruments:
            if not instrument.is_drum and 24 <= instrument.program <= 31:
                program = instrument.program
                notes_by_time = {}

                for note in instrument.notes:
                    notes_by_time.setdefault(note.start, []).append(note.pitch)

                unique_chords = set()

                for pitches in notes_by_time.values():
                    if len(pitches) >= chord_threshold:
                        chord = tuple(sorted(pretty_midi.note_number_to_name(p) for p in pitches))
                        unique_chords.add(chord)

                if unique_chords:
                    result.append({
                        "program": f"{program}",
                        "title": self.general_midi_guitar_names.get(program, f"Program {program}"),
                        "chords": [list(chord) for chord in sorted(unique_chords)]
                    })

        return result
