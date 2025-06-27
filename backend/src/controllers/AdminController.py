from src.services.DatasetService import DatasetService

def create_dataset():
    midi_dir = "/app/midi_raw_files" # from Docker container
    output_csv = r"src/dataset/midi_dataset_remake.csv"

    service = DatasetService(midi_dir, output_csv)
    service.process()
    
    return {
        "message": "new dataset created"
    }