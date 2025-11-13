import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from collections import Counter
from typing import Tuple
from pathlib import Path
import joblib
import time
import numpy as np

BASE_DIR = Path(__file__).resolve().parent                    # /app/src/services
MODELS_DIR = (BASE_DIR / '..' / 'AIModels').resolve()        # /app/src/AIModels
DATASET_DIR = (BASE_DIR / '..' / 'dataset').resolve()        # /app/src/dataset
MODEL_PATH = MODELS_DIR / 'emotion_randomforest_model.pkl'

TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'train_dataset.csv')
TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'test_dataset.csv')
MODEL_PATH = os.path.join(MODELS_DIR, 'emotion_randomforest_model.pkl')


class RandomForestService:
    def __init__(self):
        self._emotion_model = None
        self.model_path = os.path.abspath(MODEL_PATH)
        self.n_features = 0;
        self.feature_names = None;

        # check if current saved model exists
        if os.path.exists(self.model_path):
            print(f"🔹 Existent model found in: {self.model_path}")
            self.load_model()
        else:
            print("⚠️ Model didn't find. Initializing new training...")
            self.train_models()

    def train_models(self):
        if not os.path.exists(TRAIN_DATASET_PATH):
            raise FileNotFoundError(f"Train dataset not found: {TRAIN_DATASET_PATH}")

        train_df = pd.read_csv(TRAIN_DATASET_PATH)

        required_columns = ["forteclass_sequence", "emotion"]
        if not all(col in train_df.columns for col in required_columns):
            raise ValueError(f"Dataset needs more columns: {required_columns}")

        train_df = train_df.dropna(subset=['forteclass_sequence'])
        train_df = train_df[train_df['forteclass_sequence'].str.len() > 0]

        X_train = train_df['forteclass_sequence']
        y_train = train_df['emotion']

        print(f"Training with {len(X_train)} samples...")

        self._emotion_model = Pipeline([
            ("vect", CountVectorizer(token_pattern=r'[^,]+', lowercase=False)),
            ("clf", RandomForestClassifier(n_estimators=100, random_state=42))
        ])

        start = time.time()
        self._emotion_model.fit(X_train, y_train)
        print(f"✅ Trained model found in {time.time() - start:.2f}s")

        self.save_model()
        print("📦 Successfully saved model!")

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self._emotion_model, self.model_path)
        print(f"💾 Model saved in: {self.model_path}")

    def load_model(self):
        """Load pretrained RandomForest model (and metadata if available)."""
        print(f"📂 Loading model from {self.model_path} ...")

        model_package = joblib.load(self.model_path)

        if not isinstance(model_package, dict) or "model" not in model_package:
            raise ValueError("❌ Invalid model file format: missing 'model' key.")

        rf_model = model_package["model"]
        self.feature_names = model_package["feature_names"]
        self.n_features = model_package["n_features"]

        vect = CountVectorizer(token_pattern=r'[^,]+', lowercase=False)
        vect.vocabulary_ = {feat: i for i, feat in enumerate(self.feature_names)}
        vect.fixed_vocabulary_ = True  # prevent re-fitting / vocabulary drift

        self._emotion_model = Pipeline([
            ("vect", vect),
            ("clf", rf_model)
        ])

        self.model_metadata = {
            key: val for key, val in model_package.items() if key != "model"
        }

        print("✅ Model and vectorizer successfully loaded!")
        print(f"🔹 Feature count: {self.n_features}")
        print(f"🔹 Pipeline ready for prediction.")

    def predict(self, forteclass_sequence: str, mode: str) -> str:
        if not isinstance(forteclass_sequence, str):
            raise ValueError("Expected forteclass_sequence as a string (comma-separated)")

        df = pd.DataFrame([{
            'forteclass_sequence': forteclass_sequence,
            'mode': mode
        }])

        pred = self._emotion_model.predict(df)[0]
        return pred;

    def evaluate(self) -> dict:
            if not os.path.exists(TEST_DATASET_PATH):
                raise FileNotFoundError(f"Test dataset not found: {TEST_DATASET_PATH}")

            test_df = pd.read_csv(TEST_DATASET_PATH)
            test_df = test_df.dropna(subset=['forteclass_sequence'])
            test_df = test_df[test_df['forteclass_sequence'].str.len() > 0]

            X_test = test_df['forteclass_sequence']
            y_test = test_df['emotion']

            print(f"\n🔍 Evaluating with {len(X_test)} samples...")

            y_pred = self._emotion_model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            print(f"\n=== RANDOM FOREST EMOTION MODEL EVALUATION ===")
            print(f"Accuracy: {accuracy:.4f}")
            print("\nDetailed classification report:")
            print(classification_report(y_test, y_pred))

            # Return metrics
            return {
                "accuracy": round(accuracy * 100, 2),
                "samples": len(X_test),
                # "unique_emotions": sorted(y_test.unique())
            }