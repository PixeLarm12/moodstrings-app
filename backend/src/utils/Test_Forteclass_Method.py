import sys
sys.path.append('/app/src')

from services.MidiService import MidiService
import pretty_midi

def test_forteclass_method():
    # Caminho do seu arquivo MIDI de teste
    midi_path = "/app/src/dataset/G_Em_C_D.mid"
    
    try:
        # Carregar o arquivo MIDI
        with open(midi_path, "rb") as f:
            midi_data = pretty_midi.PrettyMIDI(f)
        
        # Criar instância do MidiService
        service = MidiService(midi_data=midi_data)
        
        # Testar os dois métodos
        print("🎵 Testando métodos de extração de acordes:")
        print("-" * 50)
        
        # Método original (nomes de acordes)
        chords_names = service.extract_chords()
        print(f"📝 Acordes (nomes): {chords_names}")
        
        # Novo método (forte classes)
        forte_classes = service.extract_chords_forteclass()
        print(f"🔢 Forte Classes: {forte_classes}")
        
        # Estatísticas
        names_count = len(chords_names.split(' - ')) if chords_names else 0
        forte_count = len(forte_classes.split(' - ')) if forte_classes else 0
        
        print("-" * 50)
        print(f"📊 Estatísticas:")
        print(f"   • Acordes por nomes: {names_count}")
        print(f"   • Forte Classes: {forte_count}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_forteclass_method()