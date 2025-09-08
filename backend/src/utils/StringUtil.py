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

def sanitize_chord_name(chordName: str, type: str = None) -> str:
    if chordName is None:
        return None
    
    response = '[No Name]'
    raw = chordName.lower()

    if raw.startswith('a'):
        if type is 'tab':
            response = 'A'
        else:
            response = 'Lá'
    elif raw.startswith('b'):
        if type is 'tab':
            response = 'B'
        else:
            response = 'Si'
    elif raw.startswith('c'):
        if type is 'tab':
            response = 'C'
        else:
            response = 'Dó'
    elif raw.startswith('d'):
        if type is 'tab':
            response = 'D'
        else:
            response = 'Ré'
    elif raw.startswith('e'):
        if type is 'tab':
            response = 'E'
        else:
            response = 'Mi'
    elif raw.startswith('f'):
        if type is 'tab':
            response = 'F'
        else:
            response = 'Fá'
    elif raw.startswith('g'):
        if type is 'tab':
            response = 'G'
        else:
            response = 'Sol'
    
    if response == '[No Name]':
        return response

    raw = chordName[1:]

    if raw.find('min') != -1 or raw.find('minor') != -1:
        if type is 'tab':
            response += 'm'
        else:
            response += ' Menor'
    else:
        if type is 'tab':
            response += 'maj'
        else:
            response += ' Maior'

    if raw.find('#') != -1 or raw.find('sus') != -1:
        if type is 'tab':
            response += '#' 
        else:
            response += ' Sustenido'
    elif raw.find('b') != -1:
        if type is 'tab':
            response += 'b'
        else:
            response += ' Bemol'

    if raw.find('9') != -1:
        if type is 'tab':
            response += '9'
        else:
            response += ' com Nona'
    elif raw.find('7') != -1:
        if type is 'tab':
            response += '7'
        else:
            response += ' com Sétima'

    return response

def get_chord_note_names(notes):
    return [f"{note} ({sanitize_chord_name(note)})" for note in notes]

def get_mode_name(mode: str) -> str:
    raw = mode.lower()

    if raw == 'minor':
        return "Menor"
    elif raw == 'major':
        return "Maior"
    else:
        return raw
    
def classify_tempo(tempo: str) -> str:
    try:
        bpm = int(''.join(filter(str.isdigit, tempo)))
    except ValueError:
        return None, None 

    if bpm < 24:
        nome = "Larghissimo"
    elif 25 <= bpm <= 45:
        nome = "Grave"
    elif 46 <= bpm <= 60:
        nome = "Largo"
    elif 61 <= bpm <= 66:
        nome = "Lento"
    elif 67 <= bpm <= 76:
        nome = "Adagio"
    elif 77 <= bpm <= 108:
        nome = "Andante"
    elif 109 <= bpm <= 120:
        nome = "Moderato"
    elif 121 <= bpm <= 168:
        nome = "Allegro"
    elif 169 <= bpm <= 176:
        nome = "Vivace"
    elif 177 <= bpm <= 200:
        nome = "Presto"
    else:
        nome = "Prestissimo"

    return bpm, nome


