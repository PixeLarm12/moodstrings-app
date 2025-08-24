import os

def getFileExtension(file):
    _, extension = os.path.splitext(file.filename)
    return extension

def getFileName(file):
    filename, _ = os.path.splitext(file.filename)
    return filename

def redirectByFileType(file):
    extension = getFileExtension(file)
    redirect = 'midi'

    if extension == '.mp3':
        redirect = 'transcribe'

    return redirect