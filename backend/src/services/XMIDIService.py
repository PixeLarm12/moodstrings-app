import os
from src.services.MidiService import MidiService
import glob
import re
import csv
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent                    # /app/src/services
DATASET_DIR = (BASE_DIR / '..' / 'xmidi-dataset').resolve()    # /app/src/xmidi-dataset

DATASET_RAW_PATH = os.path.join(DATASET_DIR, 'five_classes_dataset_raw.csv')

class XMIDIService:
    def __init__(self):
        if os.path.exists(DATASET_RAW_PATH):
            print(f"🔹 Found dataset at: {DATASET_RAW_PATH}")
        else:
            print(f"🔹 Creating dataset in: {DATASET_RAW_PATH}")
            self.build_dataset()

    def build_dataset(self, source_dir: str = "./midi_raw_files", allowed_emotions=None, overwrite: bool = False) -> str:
        if allowed_emotions is None:
            allowed_emotions = ["angry", "romantic", "sad", "happy", "warm"]

        # ensure folder exists
        midi_folder = Path(source_dir)
        if not midi_folder.exists() or not midi_folder.is_dir():
            raise FileNotFoundError(f"Source MIDI folder not found: {midi_folder.resolve()}")

        # if dataset already exists and not overwrite, skip
        if os.path.exists(DATASET_RAW_PATH) and not overwrite:
            print(f"🔹 Dataset already exists at {DATASET_RAW_PATH} (use overwrite=True to rebuild).")
            return DATASET_RAW_PATH

        midi_paths = sorted(glob.glob(str(midi_folder / "*.mid")) + glob.glob(str(midi_folder / "*.midi")))
        print(f"🔎 Found {len(midi_paths)} midi files in {midi_folder}")

        rows = []
        errors = []
        good = 0

        # filename pattern: XMIDI_<emotion>_<genre>_<ID>.midi
        # we'll be permissive: split by underscore after XMIDI
        filename_re = re.compile(r"^XMIDI_([^_]+)_([^_]+)_([^_]+)\.(mid|midi)$", flags=re.IGNORECASE)

        for i, path in enumerate(midi_paths, start=1):
            fname = os.path.basename(path)
            m = filename_re.match(fname)
            if not m:
                # try a looser parse (split)
                parts = fname.split("_")
                if len(parts) >= 4 and parts[0].upper() == "XMIDI":
                    emotion = parts[1].lower()
                    genre = parts[2].lower()
                    id_with_ext = "_".join(parts[3:])
                    id_ = os.path.splitext(id_with_ext)[0]
                else:
                    errors.append((fname, "filename_not_match"))
                    continue
            else:
                emotion = m.group(1).lower()
                genre = m.group(2).lower()
                id_ = os.path.splitext(m.group(3))[0]

            if emotion not in allowed_emotions:
                # skip non-wanted emotions
                continue

            try:
                # Read file binary and pass to MidiService so it can create PrettyMIDI from bytes
                with open(path, "rb") as f:
                    midi_bytes = f.read()

                midi_srv = MidiService(midi_data=midi_bytes)

                # extract forteclass chord progression string
                chord_seq = midi_srv.extract_chord_progression_forteclass()

                # if empty or too short, skip
                if not chord_seq or len(chord_seq.strip()) == 0:
                    errors.append((fname, "empty_chord_sequence"))
                    continue

                # compute num chords
                num_chords = len([t for t in chord_seq.split(",") if t.strip() != ""])

                # bpm
                bpm = midi_srv.get_estimated_bpm() if hasattr(midi_srv, "get_estimated_bpm") else midi_srv.find_tempo()

                # key info (use find_estimate_key() which returns dict with tonic and mode)
                try:
                    key_info = midi_srv.find_estimate_key()
                    key_name = key_info.get("key", "")
                    tonic = key_info.get("tonic", "")
                    mode = key_info.get("mode", "")
                except Exception:
                    key_name = ""
                    tonic = ""
                    mode = ""

                rows.append({
                    "chord_sequence": chord_seq,
                    "num_chords": num_chords,
                    "emotion": emotion,
                    "genre": genre,
                    "ID": id_,
                    "bpm": float(bpm) if bpm is not None else None,
                    "key": key_name,
                    "tonic": tonic,
                    "mode": mode
                })

                good += 1
                if (good % 50) == 0:
                    print(f"  - processed {good} files...")

            except Exception as e:
                errors.append((fname, str(e)))
                # continue processing other files
                continue

        # save CSV
        os.makedirs(os.path.dirname(DATASET_RAW_PATH), exist_ok=True)
        columns = ["chord_sequence", "num_chords", "emotion", "genre", "ID", "bpm", "key", "tonic", "mode"]
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(DATASET_RAW_PATH, index=False)

        print(f"\n✅ Finished dataset build. Saved {len(df)} rows to: {DATASET_RAW_PATH}")
        if errors:
            print(f"⚠️ {len(errors)} files skipped or errored. Example: {errors[:6]}")
        return DATASET_RAW_PATH
