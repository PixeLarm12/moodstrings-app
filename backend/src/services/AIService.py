from src.services.RandomForestService import RandomForestService
from src.utils.StringUtil import get_emotion_portuguese

class AIService:
    def __init__(self):
        self.rf_service = RandomForestService() 

    def predict_emotion_from_forteclass(self, forte_sequence: str) -> str:
        emotion = self.rf_service.predict(forte_sequence)

        return get_emotion_portuguese(emotion)
