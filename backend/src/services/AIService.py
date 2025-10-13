from src.services.NaiveBayesService import NaiveBayesService
from src.services.RandomForestService import RandomForestService
from src.services.KNNService import KNNService
from src.services.SVMService import SVMService
from src.utils.StringUtil import get_emotion_portuguese

class AIService:
    def rf_predict(self, forte_sequence: str) -> str:
        rf_service = RandomForestService() 
        emotion = rf_service.predict(forte_sequence)
        evaluation = rf_service.evaluate() 

        return {
            "model_used": "Random Forest",
            "content": get_emotion_portuguese(emotion),
            "evaluation": evaluation
        }
    
    def nb_predict(self, forte_sequence: str) -> str:
        nb_service = NaiveBayesService()
        emotion = nb_service.predict(forte_sequence)
        evaluation = nb_service.evaluate() 

        return {
            "model_used": "Naive Bayes",
            "content": get_emotion_portuguese(emotion),
            "evaluation": evaluation
        }
    
    def knn_predict(self, forte_sequence: str) -> str:
        knn_service = KNNService()
        emotion = knn_service.predict(forte_sequence)
        # evaluation = knn_service.evaluate() 

        return {
            "model_used": "KNN",
            "content": get_emotion_portuguese(emotion),
            # "evaluation": evaluation
        }
    
    def svm_predict(self, forte_sequence: str) -> str:
        svm_service = SVMService()
        emotion = svm_service.predict(forte_sequence)
        evaluation = svm_service.evaluate() 

        return {
            "model_used": "SVM",
            "content": get_emotion_portuguese(emotion),
            "evaluation": evaluation
        }

