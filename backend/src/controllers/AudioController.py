from src.validators import FileValidator

def upload(file):
    response = FileValidator.validate(file)

    print(response)
