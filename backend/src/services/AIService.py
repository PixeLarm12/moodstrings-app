from src.services.NaiveBayesService import NaiveBayesService
from src.services.RandomForestService import RandomForestService
from src.services.KNNService import KNNService
from src.utils.StringUtil import get_emotion_portuguese

class AIService:
    def rf_predict(self, forte_sequence: str) -> str:
        rf_service = RandomForestService() 
        emotion = rf_service.predict(forte_sequence)

        return get_emotion_portuguese(emotion)
    
    def nb_predict(self, forte_sequence: str) -> str:
        nb_service = NaiveBayesService()
        emotion = nb_service.predict(forte_sequence)

        return get_emotion_portuguese(emotion)
    
    def knn_predict(self, forte_sequence: str) -> str:
        knn_service = KNNService()
        emotion = knn_service.predict(forte_sequence)

        return get_emotion_portuguese(emotion)
