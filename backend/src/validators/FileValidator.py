from src.enums import FileEnum
from src.utils import FileUtil

def validate(file):
    content_type = file.content_type
    file_extension = FileUtil.getFileExtension(file)

    errors = []

    if not content_type:
        errors.append({"message": "Content type not found."})
    elif not file_extension:
        errors.append({"message": "File extension not found."})
    elif content_type != "audio/mpeg" and content_type != "audio/webm" and content_type != "audio/mid":
        errors.append({"message": "Content type not valid."})
    elif file_extension != ".mp3" and file_extension != ".webm" and file_extension != ".mid" and file_extension != ".midi":
        errors.append({"message": "File extension not valid (mp3, midi, webm)"})
    elif (content_type == "audio/mpeg" and file_extension != ".mp3") or (content_type != "audio/mpeg" and file_extension == ".mp3"):
        errors.append({"message": "Content type mp3 does not corresponds for mp3 file"})
    elif (content_type == "audio/webm" and file_extension != ".webm") or (content_type != "audio/webm" and file_extension == ".webm"):
        errors.append({"message": "Content type mp3 does not corresponds for webm file"})
    elif (content_type == "audio/mid" and (file_extension != ".mid" or file_extension != ".midi")) or (content_type != "audio/mid" and (file_extension == ".mid" or file_extension == ".midi")):
        errors.append({"message": "Content type mp3 does not corresponds for midi file"})
    
    return errors