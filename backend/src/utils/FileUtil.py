import os

def getFileExtension(file):
    _, extension = os.path.splitext(file.filename)
    return extension

def getFileName(file):
    filename, _ = os.path.splitext(file.filename)
    return filename