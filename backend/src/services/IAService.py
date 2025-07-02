import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from typing import Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, '..', 'dataset', 'dataset_normalized.csv')

class IAService:
    def __init__(self, dataset_path: str = DATASET_PATH):
        self.dataset_path = os.path.abspath(dataset_path)
        self._emotion_model = None
        self._genre_model = None

        self._load_and_train_models()

    def _load_and_train_models(self):
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)

        if "progression" not in df.columns or "emotion" not in df.columns or "genre" not in df.columns:
            raise ValueError("The .csv need these columns: progression, emotion, genre")

        # Limit to 20% of dataset - performance
        df = df.sample(frac=0.1, random_state=42)

        X = df['progression']
        y_emotion = df['emotion']
        y_genre = df['genre']

        self._emotion_model = Pipeline([
            ("vect", CountVectorizer()),
            ("clf", RandomForestClassifier(n_estimators=100, random_state=42))
        ])

        self._genre_model = Pipeline([
            ("vect", CountVectorizer()),
            ("clf", RandomForestClassifier(n_estimators=100, random_state=42))
        ])

        self._emotion_model.fit(X, y_emotion)
        self._genre_model.fit(X, y_genre)

    def predict(self, progression: str) -> Tuple[str, str]:
        if not progression or len(progression.strip()) == 0:
            raise ValueError("Chord progression is null or invalid")

        pred_emotion = self._emotion_model.predict([progression])[0]
        pred_genre = self._genre_model.predict([progression])[0]

        return pred_emotion, pred_genre
