from src.enums import FileEnum
from src.utils import FileUtil

def validate(file):
    content_type = file.content_type
    file_extension = FileUtil.getFileExtension(file)

    # NOT WORKING PROPERLY
    # if content_type != FileEnum.ContentTypes.AUDIO_MIDI.value:
    #     return { "errors" : "ContentType must be audio/mid type"}
    
    # if file_extension == FileEnum.Extensions.MID.value and file_extension == FileEnum.Extensions.MIDI.value:
    #     return { "errors" : "FileExtension must be .mid or .midi"}
    
    return False