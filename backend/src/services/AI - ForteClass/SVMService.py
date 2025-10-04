import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score
from typing import Tuple
import joblib
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DATASET_PATH = os.path.join(BASE_DIR, '..', '..', 'dataset', 'forteclass_train_test', 'train_dataset.csv')
TEST_DATASET_PATH = os.path.join(BASE_DIR, '..', '..', 'dataset', 'forteclass_train_test', 'test_dataset.csv')
MODELS_DIR = os.path.join(BASE_DIR, '..', '..', 'AIModels')
#96202 amostras
class SVMService:
    def __init__(self, train_path: str = TRAIN_DATASET_PATH, test_path: str = TEST_DATASET_PATH):
        self.train_path = os.path.abspath(train_path)
        self.test_path = os.path.abspath(test_path)
        self._emotion_model = None
        
        self.train_models()
    
    def train_models(self):
        """Treina o modelo LinearSVC para emoções"""
        # Carregar dataset de treino
        if not os.path.exists(self.train_path):
            raise FileNotFoundError(f"Dataset de treino não encontrado: {self.train_path}")
        
        train_df = pd.read_csv(self.train_path)
        
        # Verificar colunas necessárias
        required_columns = ["forteclass_sequence", "emotion"]
        if not all(col in train_df.columns for col in required_columns):
            raise ValueError(f"O dataset precisa ter as colunas: {required_columns}")
        
        # Remover linhas com forteclass_sequence vazio ou NaN
        train_df = train_df.dropna(subset=['forteclass_sequence'])
        train_df = train_df[train_df['forteclass_sequence'].str.len() > 0]

        # Preparar dados de treino
        X_train = train_df['forteclass_sequence']
        y_emotion_train = train_df['emotion']
        
        print(f"Treinando com {len(X_train)} amostras")
        print(f"Emoções únicas: {sorted(y_emotion_train.unique())}")
        
        # Criar pipeline do modelo LinearSVC
        self._emotion_model = Pipeline([
            ("vect", CountVectorizer(token_pattern=r'[^,]+', lowercase=False, max_features=10000)),
            ("clf", LinearSVC(C=1.0, random_state=42, max_iter=20000))
        ])

        print("Vocabulário sendo criado...")
        print("Treinando modelo de emoção com LinearSVC...")
        start_time = time.time()
        self._emotion_model.fit(X_train, y_emotion_train)
        print(f"Modelo LinearSVC de emoção treinado em {time.time() - start_time:.2f} segundos")
        
        # Salvar modelo automaticamente
        self.save_model()
        print("Treinamento concluído!")
    
    def evaluate_model(self):
        """Avalia o modelo usando o dataset de teste"""
        if not os.path.exists(self.test_path):
            raise FileNotFoundError(f"Dataset de teste não encontrado: {self.test_path}")
        
        test_df = pd.read_csv(self.test_path)
        
        # Remover linhas com forteclass_sequence vazio
        test_df = test_df.dropna(subset=['forteclass_sequence'])
        test_df = test_df[test_df['forteclass_sequence'].str.len() > 0]
        
        X_test = test_df['forteclass_sequence']
        y_emotion_test = test_df['emotion']
        
        print(f"\nTestando com {len(X_test)} amostras")
        
        # Predições
        emotion_pred = self._emotion_model.predict(X_test)
        
        # Métricas de emoção
        emotion_accuracy = accuracy_score(y_emotion_test, emotion_pred)
        print(f"\n=== AVALIAÇÃO MODELO LinearSVC DE EMOÇÃO ===")
        print(f"Acurácia: {emotion_accuracy:.4f}")
        print("\nRelatório detalhado:")
        print(classification_report(y_emotion_test, emotion_pred))
        
        return {
            'emotion_accuracy': emotion_accuracy,
            'emotion_predictions': emotion_pred
        }
    
    def predict(self, forteclass_sequence: str) -> str:
        """Prediz emoção baseado na sequência de forte classes"""
        if not forteclass_sequence or len(forteclass_sequence.strip()) == 0:
            raise ValueError("Sequência de forte classes é nula ou inválida")
        
        if self._emotion_model is None:
            raise ValueError("Modelo não foi treinado")
        
        pred_emotion = self._emotion_model.predict([forteclass_sequence])[0]
        
        return pred_emotion
    
    def save_model(self, model_path: str = None):
        """Salva o modelo treinado"""
        if model_path is None:
            model_path = os.path.join(MODELS_DIR, "emotion_linear_svc_model.pkl")
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        joblib.dump(self._emotion_model, model_path)
        print(f"Modelo LinearSVC salvo em: {model_path}")

    def load_model(self, model_path: str = None):
        """Carrega modelo previamente salvo"""
        if model_path is None:
            model_path = os.path.join(MODELS_DIR, "emotion_linear_svc_model.pkl")
        
        self._emotion_model = joblib.load(model_path)
        print("Modelo LinearSVC carregado com sucesso!")

# Exemplo de uso
if __name__ == "__main__":
    # Treinar e avaliar
    service = SVMService()
    
    # Avaliar performance
    results = service.evaluate_model()
    
    # Teste de predição
    test_sequence = "3-3,3-4,3-5,4-14,3-2"
    try:
        emotion = service.predict(test_sequence)
        print(f"\n=== TESTE DE PREDIÇÃO LinearSVC ===")
        print(f"Sequência: {test_sequence}")
        print(f"Emoção predita: {emotion}")
    except Exception as e:
        print(f"Erro na predição : {e}")
