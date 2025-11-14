import os
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
import joblib

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = (BASE_DIR / '..' / 'TrainedModels').resolve()
DATASET_DIR = (BASE_DIR / '..' / 'lucas-dataset').resolve()

RAW_DATASET_PATH = os.path.join(DATASET_DIR, 'raw_dataset.csv')  
TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'train_dataset.csv')
TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'test_dataset.csv')
RF_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_v1.pkl')

class AITrainingService:

    def __init__(self, split: bool = False):
        self.rf_model_path = os.path.abspath(RF_MODEL_PATH)

        # first of all, split raw_dataset into test_dataset.csv (15%) and train_dataset.csv (85%)
        if not split:
            if os.path.exists(self.rf_model_path):
                print(f"🔹 Existing model found at: {self.rf_model_path}")
                self.load_model()
            else:
                print("⚠️ Model not found — training a new one...")
                self.train_model()
        else:
            self.split_raw_dataset()

    # -------------------------------------------------------------
    # SPLIT RAW DATASET
    # -------------------------------------------------------------
    def split_raw_dataset(self, test_size=0.15, random_state=42) -> dict:
        if not os.path.exists(RAW_DATASET_PATH):
            raise FileNotFoundError(f"Raw dataset not found: {RAW_DATASET_PATH}")

        df = pd.read_csv(RAW_DATASET_PATH)

        print(f"📊 Loaded RAW dataset: {df.shape[0]} samples")
        print(f"📤 Splitting into train/test ({int((1 - test_size) * 100)}% / {int(test_size * 100)}%)")

        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df["emotion"]
        )

        train_df.to_csv(TRAIN_DATASET_PATH, index=False)
        test_df.to_csv(TEST_DATASET_PATH, index=False)

        print(f"✅ Train dataset saved: {TRAIN_DATASET_PATH} ({train_df.shape[0]} samples)")
        print(f"🧪 Test dataset saved:  {TEST_DATASET_PATH} ({test_df.shape[0]} samples)")

        return {
            "train_samples": train_df.shape[0],
            "test_samples": test_df.shape[0]
        }

    # -------------------------------------------------------------
    # TRAIN
    # -------------------------------------------------------------
    def train_model(self):
        if not os.path.exists(TRAIN_DATASET_PATH):
            print("⚠️ Training dataset missing — splitting raw first.")
            self.split_raw_dataset()

        train_df = pd.read_csv(TRAIN_DATASET_PATH)
        print(f"📚 Training with {train_df.shape[0]} samples...")

        # ---------- FEATURES ----------
        # Combine forteclass + mode (possible future: add tonic)
        X = train_df["forteclass_sequence"] + " | " + train_df["mode"]
        y = train_df["emotion"]

        print("🔧 Building pipeline (CountVectorizer + RandomForest)...")

        vectorizer = CountVectorizer(
            analyzer="word",
            ngram_range=(1, 4),
            token_pattern=r"[^, ]+"   # forteclasses separated by commas
        )

        rf = RandomForestClassifier(
            n_estimators=500,
            max_depth=None,
            n_jobs=-1,
            class_weight="balanced"
        )

        pipeline = Pipeline([
            ("vect", vectorizer),
            ("clf", rf)
        ])

        print("🚀 Training model...")
        pipeline.fit(X, y)
        print("✅ Training complete!")

        # Save unwrapped objects, like your loader expects
        package = {
            "vectorizer": pipeline.named_steps["vect"],
            "model": pipeline.named_steps["clf"]
        }

        os.makedirs(os.path.dirname(self.rf_model_path), exist_ok=True)
        joblib.dump(package, self.rf_model_path)

        print(f"💾 Model saved in: {self.rf_model_path}")

        # Store in memory
        self._emotion_model = pipeline

    # -------------------------------------------------------------
    # LOAD
    # -------------------------------------------------------------
    def load_model(self):
        package = joblib.load(self.rf_model_path)

        self._emotion_model = Pipeline([
            ('vect', package['vectorizer']),
            ('clf', package['model'])
        ])

        print("✅ Model loaded and ready for prediction")

    # -------------------------------------------------------------
    # EVALUATE
    # -------------------------------------------------------------
    def evaluate(self) -> dict:
        if not os.path.exists(TEST_DATASET_PATH):
            raise FileNotFoundError(f"Test dataset missing: {TEST_DATASET_PATH}")

        if not hasattr(self, "_emotion_model"):
            self.load_model()

        test_df = pd.read_csv(TEST_DATASET_PATH)
        print(f"🧪 Evaluating on {test_df.shape[0]} samples...")

        X_test = test_df["forteclass_sequence"] + " | " + test_df["mode"]
        y_test = test_df["emotion"]

        print("🔍 Running predictions on test set...")
        y_pred = self._emotion_model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        print(f"🎯 Accuracy: {acc:.4f}")

        report = classification_report(y_test, y_pred, output_dict=True)
        print("\n📄 Classification Report:")
        print(classification_report(y_test, y_pred))

        return {
            "accuracy": acc,
            "report": report,
            "total_test_samples": test_df.shape[0]
        }

