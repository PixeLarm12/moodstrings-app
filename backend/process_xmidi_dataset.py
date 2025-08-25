#!/usr/bin/env python3
"""
Script simples para extrair forte classes dos primeiros 15 arquivos MIDI
Dataset: C:\temp\XMIDI_Dataset
"""

import os
import re
import pandas as pd
import pretty_midi
from music21 import chord
from pathlib import Path

def extract_forte_classes(midi_file_path):
    """
    Extrai forte classes de um arquivo MIDI
    """
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_file_path)
        forte_classes = []
        
        for instrument in midi_data.instruments:
            if not instrument.is_drum:
                notes_by_time = {}
                
                # Agrupar notas por tempo
                bucket_size = 0.25
                for note in instrument.notes:
                    bucket = round(note.start / bucket_size) * bucket_size
                    notes_by_time.setdefault(bucket, []).append(note.pitch)
                
                # Extrair acordes
                prev_forte = None
                for time in sorted(notes_by_time.keys()):
                    pitches = notes_by_time[time]
                    if len(pitches) >= 2:  # Pelo menos 2 notas para ser acorde
                        note_names = [pretty_midi.note_number_to_name(p) for p in pitches]
                        
                        try:
                            objChord = chord.Chord(note_names)
                            forte_class = objChord.forteClassTn
                            
                            if forte_class is not None and forte_class != prev_forte:
                                forte_classes.append(forte_class)
                                prev_forte = forte_class
                        except:
                            continue
        
        return forte_classes
        
    except Exception as e:
        print(f"Erro: {e}")
        return []

def main():
    # Pasta do dataset (mapeada pelo Docker)
    dataset_folder = "/app/midi_raw_files"
    
    print("🎵 Extraindo Forte Classes")
    print("=" * 40)
    
    # Verificar se pasta existe
    if not os.path.exists(dataset_folder):
        print(f"❌ Pasta não encontrada: {dataset_folder}")
        return
    
    # Listar arquivos MIDI
    midi_files = []
    for file in os.listdir(dataset_folder):
        if file.endswith('.midi') or file.endswith('.mid'):
            midi_files.append(file)
    
    print(f"📁 Encontrados {len(midi_files)} arquivos MIDI")
    
    if len(midi_files) == 0:
        print("❌ Nenhum arquivo MIDI encontrado!")
        return
    
    # Pegar apenas os primeiros 15
    sample_files = midi_files[:15]
    print(f"🎯 Processando {len(sample_files)} arquivos...")
    print()
    
    results = []
    
    for i, filename in enumerate(sample_files):
        print(f"{i+1:2d}. {filename}")
        
        # Extrair info do nome do arquivo
        match = re.match(r'XMIDI_(\w+)_(\w+)_([a-zA-Z0-9]{8})\.midi?', filename)
        if match:
            emotion, genre, file_id = match.groups()
        else:
            emotion, genre, file_id = "unknown", "unknown", "unknown"
        
        # Processar arquivo
        file_path = os.path.join(dataset_folder, filename)
        forte_classes = extract_forte_classes(file_path)
        forte_sequence = ','.join(map(str, forte_classes))
        
        print(f"    Emoção: {emotion} | Gênero: {genre}")
        print(f"    Forte Classes: {forte_sequence}")
        print(f"    Total: {len(forte_classes)} classes")
        print()
        
        results.append({
            'filename': filename,
            'emotion': emotion,
            'genre': genre,
            'file_id': file_id,
            'forteclass_sequence': forte_sequence,
            'num_classes': len(forte_classes)
        })
    
    # Salvar CSV
    df = pd.DataFrame(results)
    output_file = "dataset_forteclass_15.csv"
    df.to_csv(output_file, index=False)
    
    print("✅ Processamento concluído!")
    print(f"📄 Arquivo salvo: {output_file}")
    print(f"📊 {len(results)} arquivos processados")

if __name__ == "__main__":
    main()
