from src.services.DatasetService import DatasetService

def create_dataset():
    midi_dir = "/app/midi_raw_files" # from Docker container
    output_csv = r"src/dataset/midi_dataset_remake.csv"

    service = DatasetService(midi_dir, output_csv)
    service.process()
    
    return {
        "message": "new dataset created"
    }

def normalize_dataset():
    midi_dir = r"src/dataset/midi_dataset_remake.csv"
    output_csv = r"src/dataset/dataset_normalized.csv"

    service = DatasetService(midi_dir, output_csv)
    service.normalize_dataset(midi_dir, output_csv)
    
    return {
        "message": "normalized dataset!"
    }