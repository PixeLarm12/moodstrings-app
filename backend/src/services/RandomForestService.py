import os
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import FeatureUnion
import joblib
import numpy as np

BASE_DIR = Path(__file__).resolve().parent                   
MODELS_DIR = (BASE_DIR / '..' / 'final-models').resolve()
DATASET_DIR = (BASE_DIR / '..' / 'final-dataset').resolve()

BALANCED_CHUNKED_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_chunked_40_strict_dataset.csv')  
BALANCED_CHUNKED_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_chunked_40_strict_train_dataset.csv')
BALANCED_CHUNKED_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'chunked_40_strict_test_dataset.csv')
RF_BALANCED_CHUNKED_PATH = os.path.join(MODELS_DIR, 'random_forest_balanced_chunked_40_strict_model.pkl')

FULL_DATASET_DATASET_PATH = os.path.join(DATASET_DIR, 'full_dataset.csv')  
FULL_DATASET_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'full_train_dataset.csv')
FULL_DATASET_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'full_test_dataset.csv')
RF_FULL_PATH = os.path.join(MODELS_DIR, 'random_forest_full_model.pkl')

class RandomForestService:
    def __init__(self):
        self._emotion_model = None
        # self.model_path = os.path.abspath(RF_BALANCED_CHUNKED_PATH)
        self.model_path = os.path.abspath(RF_FULL_PATH)
        self.vectorizer = None
        self.classifier = None

        if os.path.exists(self.model_path):
            print(f"🔹 Found trained model at: {self.model_path}")
            self._emotion_model = joblib.load(RF_FULL_PATH)
            # self.load_balanced_model()
        else:
            raise FileNotFoundError(
                f"Trained model not found at {self.model_path}"
            )

    def load_balanced_model(self):
        if not os.path.exists(RF_BALANCED_CHUNKED_PATH):
            raise FileNotFoundError(f"Balanced chunk model not found: {RF_BALANCED_CHUNKED_PATH}")

        pkg = joblib.load(RF_BALANCED_CHUNKED_PATH)

        if "vectorizer" not in pkg or "lda" not in pkg or "model" not in pkg:
            raise ValueError("Invalid model package: missing vectorizer, lda, or model.")

        self.vectorizer = pkg["vectorizer"]
        self.lda = pkg["lda"]
        self.classifier = pkg["model"]

        # Rebuild the complete pipeline
        self._emotion_model = Pipeline([
            ("vectorizer", self.vectorizer),
            ("lda", self.lda),
            ("model", self.classifier)
        ])

        print("✅ Balanced chunk model loaded successfully.")
        print(f"   - Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        print(f"   - LDA components: {self.lda.n_components}")
        print(f"   - Classes: {list(self.classifier.classes_)}")

        return self._emotion_model


    # -----------------------
    # Predict
    # -----------------------
    def predict_balanced_chunk(self, forteclass_sequence: str, mode: str) -> dict:
        # Validate model
        if not hasattr(self, "_emotion_model") or self._emotion_model is None:
            raise ValueError("Balanced chunked model not loaded. Run load_balanced_50_model() first.")

        # Validate inputs
        if not isinstance(forteclass_sequence, str) or not isinstance(mode, str):
            raise ValueError("forteclass_sequence and mode must be strings.")

        # Combine inputs
        combined = f"{forteclass_sequence} | {mode}"
        X = [combined]

        # Predict
        pred = self._emotion_model.predict(X)[0]
        probs = self._emotion_model.predict_proba(X)[0]

        # Extract class names
        classes = list(self._emotion_model.named_steps["model"].classes_)

        return {
            "emotion": str(pred),
            "probabilities": {c: float(p) for c, p in zip(classes, probs)}
        }
    
    def predict_full_ngrams(self, forteclass_sequence: str, mode: str, tonic: str = None):
        if self._emotion_model is None:
            raise ValueError("Model not loaded.")

        # must match training format
        combined = f"{forteclass_sequence} | {mode} | {tonic}"

        pred = self._emotion_model.predict([combined])[0]
        probs = self._emotion_model.predict_proba([combined])[0]
        classes = self._emotion_model.classes_

        return {
            "emotion": str(pred),
            "probabilities": {c: float(p) for c, p in zip(classes, probs)}
        }

    # -----------------------
    # Evaluation
    # -----------------------
    def evaluate_model_balanced(self) -> dict:
        if not hasattr(self, "_emotion_model") or self._emotion_model is None:
            raise ValueError("50-chunk model not loaded. Run load_emotion_model() first.")

        if not os.path.exists(BALANCED_CHUNKED_TEST_DATASET_PATH):
            raise FileNotFoundError(
                f"Balanced 50-chunk test dataset not found: {BALANCED_CHUNKED_TEST_DATASET_PATH}"
            )

        df = pd.read_csv(BALANCED_CHUNKED_TEST_DATASET_PATH)

        # Clean rows
        df = df.dropna(subset=['forteclass_sequence', 'mode', 'emotion'])
        df = df[df['forteclass_sequence'].str.len() > 0]

        X = (df['forteclass_sequence'] + " | " + df['mode']).values
        y_true = df['emotion'].values

        print(f"🔍 Evaluating BALANCED 50-chunk model on {len(X)} samples...")

        y_pred = self._emotion_model.predict(X)

        acc = accuracy_score(y_true, y_pred) * 100
        report = classification_report(y_true, y_pred, output_dict=True)

        print(f"🎯 BALANCED 50-CHUNK Accuracy: {acc:.2f}%")
        print(classification_report(y_true, y_pred))

        return {
            "accuracy": f"{acc:.2f}",
            "report": report,
            "n_samples": len(X)
        }
    
    def evaluate_full_ngrams(self):
        df = pd.read_csv(FULL_DATASET_TEST_DATASET_PATH)
        df = df.dropna(subset=["ngrams_input", "emotion"])

        X = df["ngrams_input"].astype(str)
        y = df["emotion"].astype(str)

        preds = self._emotion_model.predict(X)
        probs = self._emotion_model.predict_proba(X)

        acc = accuracy_score(y, preds) * 100
        report = classification_report(y, preds, output_dict=True)

        print(f"🎯 Accuracy: {acc:.2f}%")
        return {
            "accuracy": acc,
            "report": report,
            "n_samples": len(df)
        }