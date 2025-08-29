import pretty_midi
import tempfile
from music21 import chord, converter, tempo
from src.utils.StringUtil import simplify_chord_name
from io import BytesIO

class MidiService:
    def __init__(self, file=None, midi_data=None):
        if midi_data:
            self._midi_data = midi_data
        elif file:
            self._midi_data = pretty_midi.PrettyMIDI(BytesIO(file.file.read()))
        else:
            raise ValueError("You must provide either a file or midi_data.")

    @property
    def midi_data(self):
        return self._midi_data

    @midi_data.setter
    def midi_data(self, value):
        self._midi_data = pretty_midi.PrettyMIDI(BytesIO(value.file.read()))

    def extract_chords(self, chord_threshold=2):
        raw_chords = []
        named_chords = [];

        for instrument in self._midi_data.instruments:
            if not instrument.is_drum:
                notes_by_time = {}

                bucket_size = 0.25
                for note in instrument.notes:
                    bucket = round(note.start / bucket_size) * bucket_size
                    notes_by_time.setdefault(bucket, []).append(note.pitch)

                previous_chord = None
                for time in sorted(notes_by_time.keys()):
                    pitches = notes_by_time[time]
                    if len(pitches) >= chord_threshold:
                        item = '+'.join(sorted(pretty_midi.note_number_to_name(p) for p in pitches))
                        if item != previous_chord:
                            raw_chords.append(item)

        prev = None
        for raw in raw_chords:
            note_names = raw.split("+")
            objChord = chord.Chord(note_names)
            sc = simplify_chord_name(objChord.pitchedCommonName)
            if sc and sc != prev:
                named_chords.append(sc)
                prev = sc

        return ' - '.join(named_chords)
    
    def extract_chords_forteclass(self, chord_threshold=2):
        """
        Extrai progressão de acordes em formato Forte Class
        Retorna string com forte classes separadas por ' - '
        """
        raw_chords = []
        forte_classes = []

        # 1. Agrupar notas por tempo (mesma lógica do extract_chords)
        for instrument in self._midi_data.instruments:
            if not instrument.is_drum:
                notes_by_time = {}

                bucket_size = 0.25
                for note in instrument.notes:
                    bucket = round(note.start / bucket_size) * bucket_size
                    notes_by_time.setdefault(bucket, []).append(note.pitch)

                previous_chord = None
                for time in sorted(notes_by_time.keys()):
                    pitches = notes_by_time[time]
                    if len(pitches) >= chord_threshold:
                        item = '+'.join(sorted(pretty_midi.note_number_to_name(p) for p in pitches))
                        if item != previous_chord:
                            raw_chords.append(item)
                            previous_chord = item

        # 2. Converter para Forte Classes
        prev_forte = None
        for raw in raw_chords:
            note_names = raw.split("+")
            try:
                objChord = chord.Chord(note_names)
                forte_class = objChord.forteClassTn
                
                # Só adiciona se forteClass não for None e não for repetido
                if forte_class is not None and forte_class != prev_forte:
                    forte_classes.append(str(forte_class))
                    prev_forte = forte_class
            except Exception:
                # Se der erro ao criar o acorde, ignora
                continue

        return ' - '.join(forte_classes)

    # Used to created dataset. Probably, use primeFormString to define some chord is better than that name.
    # def notes_to_chord_name(self, pitches: list[int]):
    #     if not pitches or len(pitches) < 2:
    #         return ""

    #     try:
    #         normalized_pitches = []
    #         for p in pitches:
    #             p_name = pretty_midi.note_number_to_name(p)[:-1]  
    #             normalized_pitches.append(p_name)

    #         c = chord.Chord(normalized_pitches)
    #         return c.root()
    #     except Exception:
    #         return '+'.join([pretty_midi.note_number_to_name(p) for p in pitches])
        

    # This function is not correct, but stuffs here could be used in future, as chordify to find correctly chords
    # def extract_chords_new(self):
    #     with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi:
    #         self._midi_data.write(tmp_midi.name)
    #         midi_path = tmp_midi.name

    #     score = converter.parse(midi_path)
    #     chords = score.chordify()

    #     named_chords = []
    #     prev = None
    #     for c in chords.recurse().getElementsByClass('Chord'):
    #         sc = simplify_chord_name(c.pitchedCommonName)
    #         if sc and sc != prev:
    #             named_chords.append(sc)
    #             prev = sc

    #     return " - ".join(named_chords)

    def create_midi_converter(self):
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi:
            self._midi_data.write(tmp_midi.name)
            midi_path = tmp_midi.name

        return converter.parse(midi_path)

    def find_tempo(self):
        midi_file = self.create_midi_converter()

        tempos = midi_file.recurse().getElementsByClass(tempo.MetronomeMark)

        response = [];

        if tempos:
            for t in tempos:
                response.append(f"{ t.number } BPM");
        else:
            print("There's no expressive tempo mark into midi file.")

        return " - ".join(response)
    
    def find_estimate_key(self):
        midi_file = self.create_midi_converter()

        key = midi_file.analyze('key')

        return {
            'key': str(key),
            'mode': key.mode,
            'tonic': str(key.tonic),
        }

