import re

def get_clean_chord_name(text) -> str:
    QUALITY_MAP = {
        "major": "",
        "minor": "m",
        "dominant": "",  # handled separately
        "diminished": "dim",
        "augmented": "aug",
    }

    EXTENSION_MAP = {
        "seventh": "7",
        "ninth": "9",
        "eleventh": "11",
        "thirteenth": "13",
    }

    if not isinstance(text, str):
        text = str(text)

    original = text.strip()
    lowered = original.lower()

    root_match = re.match(r"([a-g][b#]?)", original, re.IGNORECASE)
    if not root_match:
        return "[No Name]"  # fallback: return original input

    root = root_match.group(1)
    root = root[0].upper() + (root[1:] if len(root) > 1 else "")

    if "minor third above" in lowered:
        return f"{root}m"
    if "perfect fourth" in lowered or "perfect octave" in lowered:
        return root  # power chord / doubling
    if "quartal" in lowered or "tetramirror" in lowered:
        return root  # exotic modern voicing, fallback
    
    quality = ""
    extension = ""

    # Dominant seventh override
    if "dominant seventh" in lowered:
        return f"{root}7"

    # Identify quality
    for word, symbol in QUALITY_MAP.items():
        if word in lowered:
            quality = symbol
            break

    # Extensions
    for word, symbol in EXTENSION_MAP.items():
        if word in lowered:
            extension = symbol
            break

    # Incomplete but clear construction
    if "incomplete major-seventh" in lowered:
        return f"{root}maj7"

    # Major seventh explicit
    if "major seventh" in lowered:
        return f"{root}maj7"

    return f"{root}{quality}{extension}"

def simplify_chord_name(chord_name: str) -> str:
    if not chord_name:
        return None

    chord_name = chord_name.strip().lower()

    for keyword in ["major triad", "minor triad", "seventh chord", "major", "minor"]:
        chord_name = chord_name.replace(keyword, "").strip()

    parts = chord_name.split("-")  # assuming your input uses "-" separator
    root = parts[0].capitalize() if parts else None
    modifier = "".join(parts[1:]).replace(" ", "") if len(parts) > 1 else ""

    if "m" in modifier or "min" in modifier:
        return f"{root}m{modifier.replace('m','')}"  # keep extensions like 7, 9

    return f"{root}{modifier}"

def sanitize_chord_name(chordName: str, type: str = None) -> str:
    if chordName is None:
        return None
    
    response = '[No Name]'
    raw = chordName.lower()

    if raw.startswith('a'):
            response = 'A'
    elif raw.startswith('b'):
            response = 'B'
    elif raw.startswith('c'):
            response = 'C'
    elif raw.startswith('d'):
            response = 'D'
    elif raw.startswith('e'):
            response = 'E'
    elif raw.startswith('f'):
            response = 'F'
    elif raw.startswith('g'):
            response = 'G'
    
    if response == '[No Name]':
        return response

    raw = chordName[1:]

    if raw.find('min') != -1 or raw.find('minor') != -1 or raw == 'm':
        if type == 'tab':
            response += 'm'
        else:
            response += ' Minor'
    else:
        if type != 'tab':
            response += ' Major'

    if raw.find('#') != -1 or raw.find('sus') != -1:
        if type is 'tab':
            response += '#' 
        else:
            response += ' Sharp'
    elif raw.find('b') != -1:
        if type is 'tab':
            response += 'b'
        else:
            response += ' Flat'

    if raw.find('9') != -1:
        if type is 'tab':
            response += '9'
        else:
            response += 'Ninth'
    elif raw.find('7') != -1:
        if type is 'tab':
            response += '7'
        else:
            response += ' Seventh'

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

def get_emotion(emotion: str, lang: str = "en") -> str:
    translated = emotion

    if lang == "ptbr":
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
    else:
        if emotion == "angry":
            translated = "Angry"
        if emotion == "exciting":
            translated = "Exciting"
        if emotion == "fear":
            translated = "Fearful"
        if emotion == "funny":
            translated = "Funny/Playful"
        if emotion == "happy":
            translated = "Happy/Cheerful"
        if emotion == "lazy":
            translated = "Lazy/Relaxed"
        if emotion == "magnificent":
            translated = "Magnificent/Grand"
        if emotion == "quiet":
            translated = "Calm/Quiet/Serene"
        if emotion == "romantic":
            translated = "Romantic/Passionate"
        if emotion == "sad":
            translated = "Sad/Melancholic"
        if emotion == "warm":
            translated = "Warm/Cozy"

    return translated

def get_emotion_description(emotion: str, lang: str = "en") -> str:

    if lang == "ptbr":
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
    else:
        mapping = {
            "angry": (
                "Defined by rhythmic tension, aggressive timbres, and strong accents. "
                "Common in metal, punk, and intense trap. "
                "Representative examples include Rage Against the Machine and Slipknot, "
                "as well as action film scores with heavy percussive elements."
            ),
            "exciting": (
                "Marked by high energy, fast tempo, and ascending tonal progressions. "
                "Found in dance-pop, EDM, energetic rock, and sports soundtracks. "
                "Artists like Avicii, Imagine Dragons, and Dua Lipa illustrate this "
                "with driving grooves and explosive choruses."
            ),
            "fear": (
                "Atmospheric textures, dissonance, unpredictable dynamics, and expressive use of silence. "
                "Typical in suspense and horror scores, experimental music, and dark ambient. "
                "Composers such as Bernard Herrmann and Trent Reznor are associated "
                "with sonic palettes that evoke tension and unease."
            ),
            "funny": (
                "Light-hearted atmosphere, moderate tempo, and playful melodies. "
                "Common in swing jazz, groovy funk, and comedy soundtracks. "
                "Louis Jordan, Hermeto Pascoal, and animated cartoon themes "
                "capture this humorous and buoyant mood."
            ),
            "happy": (
                "Bright tonal progressions, clear metrics, and uplifting melodic lines. "
                "Frequent in pop, samba, funk-soul, and optimistic folk. "
                "Artists such as Stevie Wonder, Pharrell Williams, and Jorge Ben "
                "deliver a radiant and positive sonic character."
            ),
            "lazy": (
                "Relaxed atmosphere, slow tempos, and smooth timbres. "
                "Linked to lo-fi hip-hop, bossa nova, and chill jazz. "
                "Stan Getz, João Gilberto, and lo-fi playlists create a contemplative and comfortable sound environment."
            ),
            "magnificent": (
                "Majestic feel, large orchestration, rich harmony, and triumphant resolutions. "
                "Present in symphonic music, epic film scores, and choral works. "
                "Hans Zimmer, John Williams, and romantic-era composers like Tchaikovsky "
                "embody this monumental aesthetic."
            ),
            "quiet": (
                "Melodic simplicity, soft dynamics, and minimal textures. "
                "Appears in ambient, neo-classical, and intimate bossa nova. "
                "Erik Satie, Ludovico Einaudi, and Nils Frahm represent contemplative and serene soundscapes."
            ),
            "romantic": (
                "Expressive melodies, rich harmony, and warm timbres. "
                "Found in smooth R&B, boleros, pop ballads, and romantic classical repertoire. "
                "Adele, Sade, and Chopin explore this emotional spectrum with lyrical sensitivity."
            ),
            "sad": (
                "Slow tempos, minor tonalities, and melancholic melodic focus. "
                "Common in blues, acoustic indie, and introspective classical works. "
                "Billie Holiday, Radiohead, and Samuel Barber exemplify this emotional depth."
            ),
            "warm": (
                "Comforting sounds, organic textures, and gentle harmonic movement. "
                "Present in soul, acoustic folk, and MPB. "
                "Norah Jones, Elis Regina, and James Taylor illustrate a cozy and intimate aesthetic."
            ),
        }

        return mapping.get(emotion, "No musical profile registered for this emotion.")

    