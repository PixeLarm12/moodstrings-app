import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from collections import Counter
from typing import Tuple
from pathlib import Path
import joblib
import time
import numpy as np

BASE_DIR = Path(__file__).resolve().parent                    # /app/src/services
MODELS_DIR = (BASE_DIR / '..' / 'AIModels').resolve()        # /app/src/AIModels
DATASET_DIR = (BASE_DIR / '..' / 'dataset').resolve()        # /app/src/dataset
# MODEL_PATH = MODELS_DIR / 'emotion_randomforest_model.pkl'

TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'emotions_balanced_stratified.csv')
TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'emotions_balanced_stratified.csv')
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
        # Load dataset
        train_df = pd.read_csv(TRAIN_DATASET_PATH)
        train_df = train_df.dropna(subset=['forteclass_sequence', 'mode'])
        train_df = train_df[train_df['forteclass_sequence'].str.len() > 0]

        # Combine sequence + mode
        X = train_df['forteclass_sequence'] + ',' + train_df['mode']
        y = train_df['emotion']

        # 80/20 split with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"Training with {len(X_train)} samples, testing with {len(X_test)} samples...")

        # Vectorize sequences
        vect = CountVectorizer(token_pattern=r'[^,]+', lowercase=False)
        X_train_vect = vect.fit_transform(X_train)
        X_test_vect = vect.transform(X_test)

        # Train Random Forest
        clf = RandomForestClassifier(n_estimators=200, random_state=42)
        clf.fit(X_train_vect, y_train)

        # Evaluate on test set
        y_pred = clf.predict(X_test_vect)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"✅ Validation Accuracy: {accuracy:.4f}")
        print(classification_report(y_test, y_pred))

        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            "model": clf,
            "vectorizer": vect,
            "feature_names": list(vect.vocabulary_.keys())
        }, self.model_path)
        print(f"💾 Model trained and saved at {self.model_path}")



    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self._emotion_model, self.model_path)
        print(f"💾 Model saved in: {self.model_path}")

    def load_model(self):
        package = joblib.load(self.model_path)
        self._emotion_model = Pipeline([
            ('vect', package['vectorizer']),
            ('clf', package['model'])
        ])
        print("✅ Model loaded, ready for prediction")


    def predict(self, forteclass_sequence: str, mode: str, tonic: str) -> str:
        # XMIDI_sad_pop_50MDB94E.midi,sad,pop,"3-11B,3-11A,3-10,3-11B,3-11A,3-10,3-11B,2-4,2-5,2-3,2-4,2-3,2-2,2-3,2-4,2-5,2-4,2-3,2-5,2-4,2-3,2-5,2-4,2-5,2-3,2-4,2-3,2-4,2-5,2-4,2-3,2-5,2-2,2-4,2-5,2-3,2-4,2-3,2-4,2-5,2-4,2-3,2-5,2-4,2-3,2-5,2-4,2-5,2-3,2-4,2-3,2-4,2-5,2-4,2-3,2-5,2-4,2-3,2-5,2-4,2-3,2-5,2-4,2-3,3-11B,3-11A,3-10,3-11A,3-10,3-11B,3-11A,3-10,3-11A,3-10,3-11B,2-2,2-1,1-1,3-6,1-1,2-1,1-1,2-2,1-1,4-11B,1-1,3-2A,1-1,2-2,1-1,2-1,1-1,2-2,1-1,4-11B,1-1,4-11B,1-1,2-2,2-1,1-1,2-2,1-1,2-2,1-1,2-1,1-1,2-3,2-4,2-5,4-11B,1-1,2-2,2-1,1-1,2-2,1-1,3-6,1-1,3-2A,1-1,2-2,1-1,3-2A,1-1,2-2,1-1,2-1,1-1,2-1,1-1,2-3,2-4,2-5,3-6,1-1,4-11B,2-2,1-1,2-2,1-1,3-7A,1-1,2-1,1-1,3-6,1-1,2-2,1-1,2-2,1-1,2-2,1-1,3-2A,2-3,1-1,2-2,1-1,3-2A,1-1,2-2,1-1,2-1,2-3,2-2,2-1,2-5",167,D,major
        if not isinstance(forteclass_sequence, str):
            raise ValueError("Expected forteclass_sequence as a string (comma-separated)")
        
        # normalized = self.normalize_sequence(forteclass_sequence)
        # Combine sequence + mode just like training
        combined_input = f"{forteclass_sequence},{mode},{tonic}"

        # Pipeline handles vectorization + prediction
        pred = self._emotion_model.predict([combined_input])[0]
        
        self.debug_prediction(forteclass_sequence, mode)

        return pred

    def evaluate(self) -> dict:
        if not os.path.exists(TEST_DATASET_PATH):
            raise FileNotFoundError(f"Test dataset not found: {TEST_DATASET_PATH}")

        # Load CSV
        test_df = pd.read_csv(TEST_DATASET_PATH)

        # Drop rows with empty sequences
        test_df = test_df.dropna(subset=['forteclass_sequence', 'mode'])
        test_df = test_df[test_df['forteclass_sequence'].str.len() > 0]

        # Combine forteclass_sequence and mode into single string
        combined_feature = test_df['forteclass_sequence'] + "," + test_df['mode']

        # Labels
        y_test = test_df['emotion']

        print(f"\n🔍 Evaluating with {len(combined_feature)} samples...")

        # Convert Series to DataFrame with a single column (matches training)
        # X_test = pd.DataFrame({'forteclass_sequence': combined_feature})

        # Predict
        y_pred = self._emotion_model.predict(combined_feature)

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n=== RANDOM FOREST EMOTION MODEL EVALUATION ===")
        print(f"Accuracy: {accuracy:.4f}")
        print("\nDetailed classification report:")
        print(classification_report(y_test, y_pred))

        return {
            "accuracy": round(accuracy * 100, 2),
            # "samples": len(X_test),
        }
    
    def debug_prediction(self, forteclass_sequence: str, mode: str):
        """
        Debug the pipeline step by step for a single input sequence.
        Prints tokenization and final predicted probabilities.
        """
        if self._emotion_model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        print("Training vocabulary:", list(self._emotion_model.steps[0][1].vocabulary_.keys()))
        # Combine forteclass_sequence and mode like during evaluation
        combined_input = f"{forteclass_sequence},{mode}"

        # Step 1: Vectorize input
        vect = None
        clf = None
        if hasattr(self._emotion_model, 'named_steps'):
            vect = self._emotion_model.named_steps.get('vect')
            clf = self._emotion_model.named_steps.get('clf')
        else:
            # fallback if not named_steps
            if isinstance(self._emotion_model, Pipeline):
                vect = self._emotion_model.steps[0][1]
                clf = self._emotion_model.steps[1][1]
            else:
                raise ValueError("Pipeline structure not recognized.")

        X_vect = vect.transform([combined_input])
        print("✅ Vectorized input shape:", X_vect.shape)
        print("Vectorized features (non-zero indices):", X_vect.nonzero())

        # Step 2: Predict probabilities
        y_proba = clf.predict_proba(X_vect)
        print("Predicted probabilities for each class:")
        for cls, prob in zip(clf.classes_, y_proba[0]):
            print(f"  {cls}: {prob:.4f}")

        # Step 3: Predict label
        y_pred = clf.predict(X_vect)
        print("Predicted label:", y_pred[0])
        return y_pred[0]
    
    # def normalize_sequence(self, seq_str: str, target_len: int = 125) -> str:
    #     tokens = [t for t in (s.strip() for s in seq_str.split(',')) if t != ""]
    #     if not tokens:
    #         return ','.join(['PAD'] * target_len)

    #     if len(tokens) >= target_len:
    #         return ','.join(tokens[:target_len])

    #     # build blocks of the original token block
    #     out = []
    #     while len(out) < target_len:
    #         out.extend(tokens)
    #     return ','.join(out[:target_len])
