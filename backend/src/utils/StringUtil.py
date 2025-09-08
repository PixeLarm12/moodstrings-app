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

def get_chord_name_simple(chordName: str) -> str:
    response = '[No Name]'
    raw = chordName.lower()

    if raw.startswith('a'):
        response = 'Lá'
    elif raw.startswith('b'):
        response = 'Si'
    elif raw.startswith('c'):
        response = 'Dó'
    elif raw.startswith('d'):
        response = 'Ré'
    elif raw.startswith('e'):
        response = 'Mi'
    elif raw.startswith('f'):
        response = 'Fá'
    elif raw.startswith('g'):
        response = 'Sol'
    
    if response == '[No Name]':
        return response

    raw = chordName[1:]

    if raw.find('#') != -1 or raw.find('sus') != -1:
        response += ' Sustenido'
    elif raw.find('b') != -1:
        response += ' Bemol'

    if raw.find('min') != -1 or raw.find('minor') != -1:
        response += ' Menor'
    else:
        response += ' Maior'

    if raw.find('9') != -1:
        response += ' com Nona'
    elif raw.find('7') != -1:
        response += ' com Sétima'

    return response

