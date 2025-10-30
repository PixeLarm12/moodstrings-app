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
        if type != 'tab':
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

def classify_tempo(tempo) -> tuple[int, str]:
    if isinstance(tempo, (float, int)):
        bpm = int(tempo)
    else:
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

def get_emotion_pt(emotion: str) -> str:
    translated = emotion

    if emotion == "angry":
        translated = 'Irritado'
    if emotion == "exciting":
        translated = 'Empolgante/Excitante'
    if emotion == "fear":
        translated = 'Medo/Assustador'
    if emotion == "funny":
        translated = 'Engraçado/Divertido'
    if emotion == "happy":
        translated = 'Feliz/Alegre'
    if emotion == "lazy":
        translated = 'Preguiçoso/Relaxado'
    if emotion == "magnificent":
        translated = 'Magnífico/Grandioso'
    if emotion == "quiet":
        translated = 'Calmo/Silencioso/Sereno'
    if emotion == "romantic":
        translated = 'Romântico/Apaixonado'
    if emotion == "sad":
        translated = 'Triste/Melancólico'
    if emotion == "warm":
        translated = 'Aconchegante/Caloroso'

    return translated

def get_emotion_description_pt(emotion: str) -> str:
    mapping = {
        "angry": (
            "Caracteriza-se por tensão rítmica, timbres agressivos e acentuação forte. "
            "Frequentemente associado a gêneros como metal, punk e trap mais intenso. "
            "Exemplos emblemáticos incluem bandas como Rage Against the Machine e Slipknot, "
            "bem como produções cinematográficas de ação com elevada percussividade."
        ),
        "exciting": (
            "Marcas de alta energia, andamento acelerado e progressões tonais ascendentes. "
            "Comum em pop dançante, EDM, rock enérgico e trilhas esportivas. "
            "Artistas como Avicii, Imagine Dragons e Dua Lipa exemplificam esta sensação "
            "com grooves pulsantes e refrões expansivos."
        ),
        "fear": (
            "Texturas atmosféricas, dissonâncias, dinâmica imprevisível e uso expressivo de silêncio. "
            "Presente em trilhas de suspense e horror, música experimental e dark ambient. "
            "Compositores como Bernard Herrmann e Trent Reznor são frequentemente associados "
            "a sonoridades que evocam apreensão e inquietação."
        ),
        "funny": (
            "Ambiente leve, andamento moderado e melodias lúdicas. "
            "Comum em swing jazz, funk descontraído e trilhas de comédia. "
            "Louis Jordan, Hermeto Pascoal e temas animados de desenhos animados "
            "representam bem a sonoridade jovial e humorística."
        ),
        "happy": (
            "Progressões tonais brilhantes, métricas claras e melodias ascendentes. "
            "Comum em pop, samba, funk soul e folk otimista. "
            "Stevie Wonder, Pharrell Williams e artistas brasileiros como Jorge Ben "
            "trabalham essa atmosfera luminosa e positiva."
        ),
        "lazy": (
            "Atmosfera relaxada, andamentos lentos e timbres suaves. "
            "Associado a lo-fi hip hop, bossa nova e jazz chill. "
            "Stan Getz, João Gilberto e playlists de lo-fi criam um ambiente sonoro introspectivo e confortável."
        ),
        "magnificent": (
            "Toque majestoso, orquestrações amplas, harmonia rica e resoluções triunfantes. "
            "Comum em música sinfônica, trilhas épicas e corais cinematográficos. "
            "Hans Zimmer, John Williams e compositores românticos como Tchaikovsky representam esta estética monumental."
        ),
        "quiet": (
            "Simplicidade melódica, dinâmica suave e texturas minimalistas. "
            "Presente em ambient, neoclássico e bossa nova intimista. "
            "Erik Satie, Ludovico Einaudi e Nils Frahm são referências de contemplação sonora e serenidade."
        ),
        "romantic": (
            "Melodias expressivas, harmonia rica e timbres quentes. "
            "Encontrado em R&B suave, boleros, baladas pop e repertório romântico erudito. "
            "Adele, Sade e Chopin exploram essa dimensão emocional com lirismo."
        ),
        "sad": (
            "Andamento lento, tonalidades menores e foco melódico melancólico. "
            "Comum em blues, indie acústico e música erudita introspectiva. "
            "Billie Holiday, Radiohead e Samuel Barber materializam este universo emotivo."
        ),
        "warm": (
            "Sons acolhedores, textura orgânica e progressões suaves. "
            "Encontrado em soul, folk acústico e MPB. "
            "Norah Jones, Elis Regina e James Taylor exemplificam uma estética reconfortante e íntima."
        ),
    }

    return mapping.get(emotion, "Nenhum perfil musical cadastrado para esta emoção.")
