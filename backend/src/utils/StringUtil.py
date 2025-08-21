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
