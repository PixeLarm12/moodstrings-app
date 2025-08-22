def normalize_chord_name(chord: str) -> str:
    chord = chord.replace("triad", "").strip()

    if "-major" in chord:
        note = chord.replace("-major", "").strip()
        return note[0] 
    elif "-minor" in chord:
        note = chord.replace("-minor", "").strip()
        return note[0] + "m"
    else:
        return chord.strip()

def simplify_chord_name(chord_name: str) -> str:
    chord_name = chord_name.lower()

    if "major triad" in chord_name:
        return chord_name.split("-")[0].strip().capitalize()

    if "minor triad" in chord_name:
        return chord_name.split("-")[0].strip().capitalize() + "m"

    if "seventh" in chord_name or "major" in chord_name:
        return chord_name.split("-")[0].strip().capitalize()

    root = chord_name.split("-")[0].strip().capitalize()
    if root in ["C", "D", "E", "F", "G", "A", "B"]:
        return root

    return None
