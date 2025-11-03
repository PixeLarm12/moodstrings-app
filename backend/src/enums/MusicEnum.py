from enum import Enum

class Scales(Enum):
    MAJOR = {
        'C': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
        'G': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
        'D': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
        'A': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
        'E': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
        'B': ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'],
        'F': ['F', 'G', 'A', 'Bb', 'C', 'D', 'E']
    }
    
    MINOR = {
        'A': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
        'E': ['E', 'F#', 'G', 'A', 'B', 'C', 'D'],
        'D': ['D', 'E', 'F', 'G', 'A', 'Bb', 'C'],
        'G': ['G', 'A', 'Bb', 'C', 'D', 'Eb', 'F'],
        'C': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb']
    }

    RELATIVE_KEYS = {
        "C": "A",
        "G": "E",
        "D": "B",
        "A": "F#",
        "E": "C#",
        "B": "G#",
        "F#": "D#",
        "C#": "A#",
        "F": "D",
        "Bb": "G",
        "Eb": "C",
        "Ab": "F",
        "Db": "Bb",
        "Gb": "Eb",
    }

    RELATIVE_KEYS_INV = {v: k for k, v in RELATIVE_KEYS.items()}

class HarmonicFunctions(Enum):
    FUNCTIONS = [
        ("I", "Tônica"),
        ("II", "Supertônica"),
        ("III", "Mediante"),
        ("IV", "Subdominante"),
        ("V", "Dominante"),
        ("VI", "Submediante"),
        ("VII", "Sensível")
    ]