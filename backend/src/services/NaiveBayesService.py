import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
from typing import Tuple
from pathlib import Path
import joblib
import time

BASE_DIR = Path(__file__).resolve().parent                    # /app/src/services
MODELS_DIR = (BASE_DIR / '..' / 'AIModels').resolve()         # /app/src/AIModels
DATASET_DIR = (BASE_DIR / '..' / 'dataset').resolve()         # /app/src/dataset
MODEL_PATH = (MODELS_DIR / 'emotion_naivebayes_model.pkl').resolve()

TRAIN_DATASET_PATH = (DATASET_DIR / 'train_dataset.csv').resolve()
TEST_DATASET_PATH = (DATASET_DIR / 'test_dataset.csv').resolve()


class NaiveBayesService:
    def __init__(self, model_path: str = None):
        self._emotion_model = None
        self.model_path = str(model_path or MODEL_PATH)
        self.train_path = str(TRAIN_DATASET_PATH)
        self.test_path = str(TEST_DATASET_PATH)

        print(f"🧩 Naive Bayes model path: {self.model_path}")

        if os.path.exists(self.model_path):
            print("✅ Existing model found. Loading...")
            self.load_model()
        else:
            print("⚠️ Model didn't find. Initializing training...")
            self.train_models()

    def train_models(self):
        if not os.path.exists(self.train_path):
            raise FileNotFoundError(f"Train dataset not found: {self.train_path}")

        print(f"📘 Train dataset loading: {self.train_path}")
        train_df = pd.read_csv(self.train_path)

        # Verificar colunas necessárias
        required_columns = ["forteclass_sequence", "emotion"]
        if not all(col in train_df.columns for col in required_columns):
            raise ValueError(f"Dataset needs to have these columns: {required_columns}")

        # Limpeza de dados
        train_df = train_df.dropna(subset=['forteclass_sequence'])
        train_df = train_df[train_df['forteclass_sequence'].str.len() > 0]

        X_train = train_df['forteclass_sequence']
        y_emotion_train = train_df['emotion']

        print(f"🧠 Training Naive Bayes model with {len(X_train)} samples...")
        print(f"🎭 Unique emotions: {sorted(y_emotion_train.unique())}")

        # Criar pipeline
        self._emotion_model = Pipeline([
            ("vect", CountVectorizer(token_pattern=r'[^,]+', lowercase=False)),
            ("clf", MultinomialNB(alpha=1.0))
        ])

        start_time = time.time()
        self._emotion_model.fit(X_train, y_emotion_train)
        print(f"✅ Finished training in {time.time() - start_time:.2f} seconds.")

        # Salvar o modelo treinado
        self.save_model()
        print(f"💾 Naive Bayes model saved into: {self.model_path}")

    def evaluate_model(self):
        if not os.path.exists(self.test_path):
            raise FileNotFoundError(f"Test dataset not found: {self.test_path}")

        print(f"📗 Loading test dataset: {self.test_path}")
        test_df = pd.read_csv(self.test_path)

        test_df = test_df.dropna(subset=['forteclass_sequence'])
        test_df = test_df[test_df['forteclass_sequence'].str.len() > 0]

        X_test = test_df['forteclass_sequence']
        y_emotion_test = test_df['emotion']

        print(f"🧪 Testing with {len(X_test)} samples...")

        emotion_pred = self._emotion_model.predict(X_test)
        emotion_accuracy = accuracy_score(y_emotion_test, emotion_pred)

        print(f"\n=== RESULTADOS AVALIAÇÃO NAIVE BAYES ===")
        print(f"Acurácia: {emotion_accuracy:.4f}")
        print(classification_report(y_emotion_test, emotion_pred))

        return {
            "emotion_accuracy": emotion_accuracy,
            "emotion_predictions": emotion_pred
        }

    def predict(self, forteclass_sequence: str) -> str:
        if not forteclass_sequence or len(forteclass_sequence.strip()) == 0:
            raise ValueError("Forteclass sequence is null or invalid.")

        if self._emotion_model is None:
            raise ValueError("Model not loaded or trained.")

        pred_emotion = self._emotion_model.predict([forteclass_sequence])[0]
        return pred_emotion

    def predict_proba(self, forteclass_sequence: str) -> dict:
        if not forteclass_sequence or len(forteclass_sequence.strip()) == 0:
            raise ValueError("Forteclass sequence is null or invalid.")

        if self._emotion_model is None:
            raise ValueError("Model not loaded or trained.")

        probabilities = self._emotion_model.predict_proba([forteclass_sequence])[0]
        classes = self._emotion_model.classes_
        return dict(zip(classes, probabilities))

    def save_model(self, model_path: str = None):
        path = model_path or self.model_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self._emotion_model, path)

    def load_model(self, model_path: str = None):
        path = model_path or self.model_path
        self._emotion_model = joblib.load(path)
        print("✅ Naive Bayes model loaded successfully!")
