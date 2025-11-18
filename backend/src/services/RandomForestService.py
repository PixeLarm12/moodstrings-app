import os
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import FeatureUnion
import joblib
import numpy as np

BASE_DIR = Path(__file__).resolve().parent                    # /app/src/services
MODELS_DIR = (BASE_DIR / '..' / 'TrainedModels').resolve()     # /app/src/TrainedModels
DATASET_DIR = (BASE_DIR / '..' / 'lucas-dataset').resolve()    # /app/src/lucas-dataset

# old paths are kept for compatibility but not used for loading new model
TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'emotions_balanced_stratified.csv')
TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'emotions_balanced_stratified.csv')
MODEL_PATH = os.path.join(MODELS_DIR, 'emotion_randomforest_model.pkl')

# NEW paths produced by AITrainingService
NEW_MODELS_DIR = (BASE_DIR / '..' / 'TrainedModels').resolve()
NEW_DATASET_DIR = (BASE_DIR / '..' / 'lucas-dataset').resolve()

NEW_TRAIN_DATASET_PATH = os.path.join(NEW_DATASET_DIR, 'train_dataset.csv')
NEW_TEST_DATASET_PATH = os.path.join(NEW_DATASET_DIR, 'test_dataset.csv')
NEW_RF_MODEL_PATH = os.path.join(NEW_MODELS_DIR, 'random_forest_v1.pkl')

CHUNK_MODELS_DIR = (BASE_DIR / '..' / 'TrainedModels').resolve()
CHUNK_DATASET_DIR = (BASE_DIR / '..' / 'lucas-dataset').resolve()

CHUNK_TRAIN_DATASET_PATH = os.path.join(CHUNK_DATASET_DIR, 'chunk_train_dataset.csv')
CHUNK_TEST_DATASET_PATH = os.path.join(CHUNK_DATASET_DIR, 'chunk_test_dataset.csv')
CHUNK_RF_MODEL_PATH = os.path.join(CHUNK_MODELS_DIR, 'random_forest_chunked_v1.pkl')

NGRAMS_DATASET_PATH = os.path.join(DATASET_DIR, 'ngrams_dataset.csv')
NGRAMS_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'ngrams_train_dataset.csv')
NGRAMS_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'ngrams_test_dataset.csv')
RF_NGRAMS_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_ngrams_v1.pkl')

FULL_NGRAMS_DATASET_PATH = os.path.join(DATASET_DIR, 'full_ngrams_dataset.csv')  
FULL_NGRAMS_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'full_ngrams_train_dataset.csv')
FULL_NGRAMS_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'full_ngrams_test_dataset.csv')
RF_FULL_NGRAMS_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_full_ngrams_v1.pkl')

BALANCED_CHUNK_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_chunked_dataset.csv')  
BALANCED_CHUNK_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_chunked_train_dataset.csv')
BALANCED_CHUNK_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_chunked_test_dataset.csv')
RF_BALANCED_CHUNK_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_balanced_chunked_v1.pkl')

BALANCED_NGRAMS_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_ngrams_dataset.csv')  
BALANCED_NGRAMS_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_ngrams_train_dataset.csv')
BALANCED_NGRAMS_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_ngrams_test_dataset.csv')
RF_BALANCED_NGRAMS_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_balanced_ngrams_v1.pkl')

CHUNKED_50_PATH = os.path.join(DATASET_DIR, 'chunked_50_dataset.csv')  
CHUNKED_50_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'chunked_50_train_dataset.csv')
CHUNKED_50_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'chunked_50_test_dataset.csv')
RF_CHUNKED_50_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_chunked_50_v1.pkl')

class RandomForestService:
    def __init__(self):
        self._emotion_model = None
        # model we will actually use (from AITrainingService)
        # self.model_path = os.path.abspath(NEW_RF_MODEL_PATH)
        # self.model_path = os.path.abspath(CHUNK_RF_MODEL_PATH)
        # self.model_path = os.path.abspath(RF_NGRAMS_MODEL_PATH)
        # self.model_path = os.path.abspath(RF_FULL_NGRAMS_MODEL_PATH)
        # self.model_path = os.path.abspath(BALANCED_CHUNK_DATASET_PATH)
        # self.model_path = os.path.abspath(BALANCED_NGRAMS_DATASET_PATH)
        self.model_path = os.path.abspath(CHUNKED_50_PATH)
        self.vectorizer = None
        self.classifier = None

        if os.path.exists(self.model_path):
            print(f"🔹 Found trained model at: {self.model_path}")
            # self.load_model()
            # self.load_chunk_model()
            # self._emotion_model = joblib.load(RF_NGRAMS_MODEL_PATH)
            # self._emotion_model = joblib.load(RF_FULL_NGRAMS_MODEL_PATH)
            # self._emotion_model = self.load_full_ngrams_model()
            # self.load_balanced_chunk_model()
            # self._emotion_model = joblib.load(RF_BALANCED_NGRAMS_MODEL_PATH)
            self._emotion_model = joblib.load(RF_CHUNKED_50_MODEL_PATH)
        else:
            raise FileNotFoundError(
                f"Trained model not found at {self.model_path}. "
                f"Run AITrainingService.train_model() first."
            )

    # -----------------------
    # Load model saved by AITrainingService
    # -----------------------
    def load_model(self):
        """
        Expecting joblib.dump of a dict { "vectorizer": fitted_vectorizer, "model": fitted_rf }
        Reconstructs a Pipeline(self.vectorizer, self.classifier) for convenience.
        """
        pkg = joblib.load(self.model_path)

        if not isinstance(pkg, dict) or "vectorizer" not in pkg or "model" not in pkg:
            raise ValueError("Model package format invalid. Expected dict with keys 'vectorizer' and 'model'.")

        self.vectorizer = pkg["vectorizer"]
        self.classifier = pkg["model"]

        self._emotion_model = Pipeline([
            ("vect", self.vectorizer),
            ("clf", self.classifier)
        ])

        print("✅ Model + vectorizer loaded and pipeline constructed.")
        print(f"   - Vectorizer vocabulary size: {len(self.vectorizer.vocabulary_)}")
        print(f"   - Classes: {list(self.classifier.classes_)}")

    def load_chunk_model(self):
        pkg = joblib.load(CHUNK_RF_MODEL_PATH)

        if not isinstance(pkg, dict) or "vectorizer" not in pkg or "model" not in pkg:
            raise ValueError("Chunked model package is invalid. Expected dict with 'vectorizer' and 'model'.")

        self.chunk_vectorizer = pkg["vectorizer"]
        self.chunk_classifier = pkg["model"]

        # Build pipeline
        self._emotion_model = Pipeline([
            ("vect", self.chunk_vectorizer),
            ("clf", self.chunk_classifier)
        ])

        print("✅ Chunked model loaded.")
        print(f"   - Vocabulary size: {len(self.chunk_vectorizer.vocabulary_)}")
        print(f"   - Classes: {list(self.chunk_classifier.classes_)}")

    def load_balanced_chunk_model(self):
        pkg = joblib.load(RF_BALANCED_CHUNK_MODEL_PATH)

        if not isinstance(pkg, dict) or "vectorizer" not in pkg or "model" not in pkg:
            raise ValueError("Balanced chunked model package invalid. Expected dict with 'vectorizer' and 'model'.")

        self.balanced_chunk_vectorizer = pkg["vectorizer"]
        self.balanced_chunk_classifier = pkg["model"]

        # Build pipeline
        self._balanced_chunk_model = Pipeline([
            ("vect", self.balanced_chunk_vectorizer),
            ("clf", self.balanced_chunk_classifier)
        ])

        print("✅ Balanced chunked model loaded.")
        print(f"   - Vocabulary size: {len(self.balanced_chunk_vectorizer.vocabulary_)}")
        print(f"   - Classes: {list(self.balanced_chunk_classifier.classes_)}")

    def load_model_ngrams_lda(self):
        if not os.path.exists(RF_BALANCED_NGRAMS_MODEL_PATH):
            raise FileNotFoundError("NGRAMS+LDA model not found.")

        self._emotion_model = joblib.load(RF_BALANCED_NGRAMS_MODEL_PATH)
        print("✅ Loaded NGRAMS + LDA RandomForest model!")
        
    # -----------------------
    # Predict
    # -----------------------
    def predict(self, forteclass_sequence: str, mode: str, tonic: str = None) -> dict:
        """
        Predict emotion for a single sequence + mode.
        The input formatting MUST match the one used at training.
        AITrainingService used: input = forteclass_sequence + " | " + mode
        """
        if self._emotion_model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        if not isinstance(forteclass_sequence, str) or not isinstance(mode, str):
            raise ValueError("forteclass_sequence and mode must be strings.")

        # Build input exactly like the trainer (separator " | ")
        combined = f"{forteclass_sequence} | {mode}"

        # Vectorize + predict
        X = [combined]
        probs = self._emotion_model.predict_proba(X)[0]
        pred = self._emotion_model.predict(X)[0]
        classes = list(self._emotion_model.named_steps['clf'].classes_)

        # Return useful structure (label + probabilities)
        result = {
            "emotion": str(pred),
            "probabilities": {c: float(p) for c, p in zip(classes, probs)}
        }
        return result
    
    def predict_chunk(self, forteclass_sequence: str, mode: str):
        if self._chunk_model is None:
            raise ValueError("Chunked model not loaded. Run load_chunk_model() first.")

        if not isinstance(forteclass_sequence, str) or not isinstance(mode, str):
            raise ValueError("forteclass_sequence and mode must be strings.")

        combined = f"{forteclass_sequence} | {mode}"

        X = [combined]
        probs = self._chunk_model.predict_proba(X)[0]
        pred = self._chunk_model.predict(X)[0]
        classes = list(self.chunk_classifier.classes_)

        return {
            "emotion": str(pred),
            "probabilities": {c: float(p) for c, p in zip(classes, probs)}
        }

    def predict_ngrams(self, forteclass_sequence: str, mode: str, tonic: str = None):
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
    
    def predict_balanced_chunk(self, forteclass_sequence: str, mode: str) -> dict:
        if not hasattr(self, "_balanced_chunk_model") or self._balanced_chunk_model is None:
            raise ValueError("Balanced chunked model not loaded. Run load_balanced_chunk_model() first.")

        if not isinstance(forteclass_sequence, str) or not isinstance(mode, str):
            raise ValueError("forteclass_sequence and mode must be strings.")

        combined = f"{forteclass_sequence} | {mode}"

        X = [combined]
        pred = self._balanced_chunk_model.predict(X)[0]
        probs = self._balanced_chunk_model.predict_proba(X)[0]
        classes = list(self.balanced_chunk_classifier.classes_)

        return {
            "emotion": str(pred),
            "probabilities": {c: float(p) for c, p in zip(classes, probs)}
        }

    def predict_ngrams_lda(self, forteclass_sequence: str, mode: str, tonic: str = None):
        if self._emotion_model is None:
            self.load_model_ngrams_lda()

        combined = f"{forteclass_sequence} | {mode}"

        pred = self._emotion_model.predict([combined])[0]
        probs = self._emotion_model.predict_proba([combined])[0]
        classes = self._emotion_model.named_steps["clf"].classes_

        return {
            "emotion": str(pred),
            "probabilities": {c: float(p) for c, p in zip(classes, probs)}
        }

    def predict_50_chunk(self, forteclass_sequence: str, mode: str) -> dict:
        if not hasattr(self, "_emotion_model") or self._emotion_model is None:
            raise ValueError("50-chunk model not loaded. Run load_emotion_model() first.")

        if not isinstance(forteclass_sequence, str) or not isinstance(mode, str):
            raise ValueError("forteclass_sequence and mode must be strings.")

        combined = f"{forteclass_sequence} | {mode}"

        X = [combined]
        pred = self._emotion_model.predict(X)[0]
        probs = self._emotion_model.predict_proba(X)[0]
        classes = list(self._50_chunk_classifier.classes_)

        return {
            "emotion": str(pred),
            "probabilities": {c: float(p) for c, p in zip(classes, probs)}
        }


    # -----------------------
    # Evaluate using new test dataset created by AITrainingService.split_raw_dataset()
    # -----------------------
    def evaluate(self) -> dict:
        """
        Run evaluation over NEW_TEST_DATASET_PATH and return metrics dict.
        """
        if not os.path.exists(NEW_TEST_DATASET_PATH):
            raise FileNotFoundError(f"Test dataset not found: {NEW_TEST_DATASET_PATH}")

        df = pd.read_csv(NEW_TEST_DATASET_PATH)
        df = df.dropna(subset=['forteclass_sequence', 'mode'])
        df = df[df['forteclass_sequence'].str.len() > 0]

        X = (df['forteclass_sequence'] + " | " + df['mode']).values
        y_true = df['emotion'].values

        print(f"🔍 Evaluating on {len(X)} samples...")

        y_pred = self._emotion_model.predict(X)

        acc = (accuracy_score(y_true, y_pred) * 100)
        report = classification_report(y_true, y_pred, output_dict=True)

        print(f"🎯 Accuracy: {acc:.2f}")
        print(classification_report(y_true, y_pred))

        return {
            "accuracy": f"{acc:.2f}",
            "report": report,
            "n_samples": len(X)
        }
    
    def evaluate_chunk(self) -> dict:
        if self._chunk_model is None:
            raise ValueError("Chunked model not loaded. Run load_chunk_model() first.")

        if not os.path.exists(CHUNK_TEST_DATASET_PATH):
            raise FileNotFoundError(f"Chunked test dataset not found: {CHUNK_TEST_DATASET_PATH}")

        df = pd.read_csv(CHUNK_TEST_DATASET_PATH)

        # Clean rows
        df = df.dropna(subset=['forteclass_sequence', 'mode'])
        df = df[df['forteclass_sequence'].str.len() > 0]

        X = (df['forteclass_sequence'] + "," + df['mode']).values
        y_true = df['emotion'].values

        print(f"🔍 Evaluating CHUNKED model on {len(X)} samples...")

        y_pred = self._chunk_model.predict(X)

        acc = accuracy_score(y_true, y_pred) * 100
        report = classification_report(y_true, y_pred, output_dict=True)

        print(f"🎯 CHUNKED Accuracy: {acc:.2f}%")
        print(classification_report(y_true, y_pred))

        return {
            "accuracy": f"{acc:.2f}",
            "report": report,
            "n_samples": len(X)
        }

    def evaluate_ngrams(self):
        df = pd.read_csv(NGRAMS_TEST_DATASET_PATH)
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
   
    def evaluate_full_ngrams(self):
        df = pd.read_csv(FULL_NGRAMS_TEST_DATASET_PATH)
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
    
    def evaluate_balanced_chunk(self) -> dict:
        if not hasattr(self, "_balanced_chunk_model") or self._balanced_chunk_model is None:
            raise ValueError("Balanced chunked model not loaded. Run load_balanced_chunk_model() first.")

        if not os.path.exists(BALANCED_CHUNK_TEST_DATASET_PATH):
            raise FileNotFoundError(f"Balanced chunked test dataset not found: {BALANCED_CHUNK_TEST_DATASET_PATH}")

        df = pd.read_csv(BALANCED_CHUNK_TEST_DATASET_PATH)

        # clean dataset
        df = df.dropna(subset=['forteclass_sequence', 'mode', 'emotion'])
        df = df[df['forteclass_sequence'].str.len() > 0]

        X = (df['forteclass_sequence'] + " | " + df['mode']).values
        y_true = df['emotion'].values

        print(f"🔍 Evaluating BALANCED CHUNKED model on {len(X)} samples...")

        y_pred = self._balanced_chunk_model.predict(X)

        acc = accuracy_score(y_true, y_pred) * 100
        report = classification_report(y_true, y_pred, output_dict=True)

        print(f"🎯 BALANCED CHUNKED Accuracy: {acc:.2f}%")
        print(classification_report(y_true, y_pred))

        return {
            "accuracy": f"{acc:.2f}",
            "report": report,
            "n_samples": len(X)
        }
    
    def evaluate_balanced_ngrams(self):
        if self._emotion_model is None:
            self.load_model_ngrams_lda()

        if not os.path.exists(BALANCED_NGRAMS_TEST_DATASET_PATH):
            raise FileNotFoundError("Test dataset missing.")

        df = pd.read_csv(BALANCED_NGRAMS_TEST_DATASET_PATH)
        df = df.dropna(subset=["ngrams_input", "emotion"])

        X = df["ngrams_input"].tolist()
        y_true = df["emotion"].tolist()

        y_pred = self._emotion_model.predict(X)
        acc = accuracy_score(y_true, y_pred) * 100
        report = classification_report(y_true, y_pred, output_dict=True)

        print(f"🎯 Accuracy: {acc:.2f}")
        print(classification_report(y_true, y_pred))

        return {
            "accuracy": acc,
            "report": report,
            "n_samples": len(df)
        }

    def evaluate_50_chunk(self) -> dict:
        if not hasattr(self, "_emotion_model") or self._emotion_model is None:
            raise ValueError("50-chunk model not loaded. Run load_emotion_model() first.")

        if not os.path.exists(CHUNKED_50_TEST_DATASET_PATH):
            raise FileNotFoundError(
                f"50-chunk test dataset not found: {CHUNKED_50_TEST_DATASET_PATH}"
            )

        df = pd.read_csv(CHUNKED_50_TEST_DATASET_PATH)

        # Clean rows
        df = df.dropna(subset=['forteclass_sequence', 'mode', 'emotion'])
        df = df[df['forteclass_sequence'].str.len() > 0]

        X = (df['forteclass_sequence'] + " | " + df['mode']).values
        y_true = df['emotion'].values

        print(f"🔍 Evaluating 50-chunk model on {len(X)} samples...")

        y_pred = self._emotion_model.predict(X)

        acc = accuracy_score(y_true, y_pred) * 100
        report = classification_report(y_true, y_pred, output_dict=True)

        print(f"🎯 50-CHUNK Accuracy: {acc:.2f}%")
        print(classification_report(y_true, y_pred))

        return {
            "accuracy": f"{acc:.2f}",
            "report": report,
            "n_samples": len(X)
        }

    
