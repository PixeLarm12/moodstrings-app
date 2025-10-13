import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path
import joblib
import time

BASE_DIR = Path(__file__).resolve().parent                    # /app/src/services
MODELS_DIR = (BASE_DIR / '..' / 'AIModels').resolve()         # /app/src/AIModels
DATASET_DIR = (BASE_DIR / '..' / 'dataset').resolve()         # /app/src/dataset
MODEL_PATH = (MODELS_DIR / 'emotion_linear_svc_model.pkl').resolve()

TRAIN_DATASET_PATH = (DATASET_DIR / 'train_dataset.csv').resolve()
TEST_DATASET_PATH = (DATASET_DIR / 'test_dataset.csv').resolve()

MODEL_FILE = os.path.join(MODELS_DIR, "emotion_linear_svc_model.pkl")

class SVMService:
    def __init__(self, train_path: str = TRAIN_DATASET_PATH, test_path: str = TEST_DATASET_PATH):
        self.train_path = os.path.abspath(train_path)
        self.test_path = os.path.abspath(test_path)
        self.model_path = os.path.abspath(MODEL_FILE)
        self._emotion_model = None

        # Try loading existing model; train if not available or corrupted
        if os.path.exists(self.model_path):
            try:
                self.load_model()
            except Exception as e:
                print(f"⚠️ Failed to load saved LinearSVC model ({e}), retraining model...")
                self.train_models()
        else:
            print("⚠️ No existing LinearSVC model found, training a new one...")
            self.train_models()

    def train_models(self):
        """Train LinearSVC model for emotion recognition"""
        if not os.path.exists(self.train_path):
            raise FileNotFoundError(f"Training dataset not found: {self.train_path}")

        train_df = pd.read_csv(self.train_path)

        required_columns = ["forteclass_sequence", "emotion"]
        if not all(col in train_df.columns for col in required_columns):
            raise ValueError(f"Dataset must contain columns: {required_columns}")

        # Clean data
        train_df = train_df.dropna(subset=['forteclass_sequence'])
        train_df = train_df[train_df['forteclass_sequence'].str.len() > 0]

        X_train = train_df['forteclass_sequence']
        y_train = train_df['emotion']

        print(f"Training with {len(X_train)} samples")
        print(f"Unique emotions: {sorted(y_train.unique())}")

        self._emotion_model = Pipeline([
            ("vect", CountVectorizer(token_pattern=r'[^,]+', lowercase=False, max_features=10000)),
            ("clf", LinearSVC(C=1.0, random_state=42, max_iter=20000))
        ])

        print("Building vocabulary...")
        print("Training LinearSVC emotion model...")
        start_time = time.time()
        self._emotion_model.fit(X_train, y_train)
        print(f"✅ LinearSVC model trained in {time.time() - start_time:.2f} seconds")

        self.save_model()
        print("💾 Model saved successfully!")

    def evaluate_model(self):
        """Evaluate the model using the test dataset"""
        if not os.path.exists(self.test_path):
            raise FileNotFoundError(f"Test dataset not found: {self.test_path}")

        test_df = pd.read_csv(self.test_path)
        test_df = test_df.dropna(subset=['forteclass_sequence'])
        test_df = test_df[test_df['forteclass_sequence'].str.len() > 0]

        X_test = test_df['forteclass_sequence']
        y_test = test_df['emotion']

        print(f"\n🔍 Evaluating with {len(X_test)} samples...")

        y_pred = self._emotion_model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        print(f"\n=== LINEARSVC EMOTION MODEL EVALUATION ===")
        print(f"Accuracy: {acc:.4f}")
        print("\nDetailed report:")
        print(classification_report(y_test, y_pred))

        return {
            'emotion_accuracy': acc,
            'emotion_predictions': y_pred
        }

    def predict(self, forteclass_sequence: str) -> str:
        """Predict emotion based on forteclass sequence"""
        if not forteclass_sequence or len(forteclass_sequence.strip()) == 0:
            raise ValueError("Invalid or empty forteclass sequence")

        if self._emotion_model is None:
            raise ValueError("Model has not been trained or loaded")

        return self._emotion_model.predict([forteclass_sequence])[0]

    def save_model(self, model_path: str = None):
        """Save the trained model"""
        if model_path is None:
            model_path = self.model_path

        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self._emotion_model, model_path)
        print(f"💾 Model saved at: {model_path}")

    def load_model(self, model_path: str = None):
        """Load a previously saved model"""
        if model_path is None:
            model_path = self.model_path

        self._emotion_model = joblib.load(model_path)
        print(f"✅ LinearSVC model successfully loaded from: {model_path}")

    def evaluate(self) -> dict:
            """
            Evaluates the trained LinearSVC model on the test dataset.
            Returns a dictionary with accuracy, number of test samples, and unique emotions.
            """
            if not os.path.exists(self.test_path):
                raise FileNotFoundError(f"Test dataset not found: {self.test_path}")

            print(f"📗 Loading test dataset: {self.test_path}")
            test_df = pd.read_csv(self.test_path)

            # Clean dataset
            test_df = test_df.dropna(subset=['forteclass_sequence'])
            test_df = test_df[test_df['forteclass_sequence'].str.len() > 0]

            X_test = test_df['forteclass_sequence']
            y_test = test_df['emotion']

            print(f"🧪 Evaluating with {len(X_test)} samples...")

            y_pred = self._emotion_model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)

            print(f"\n=== LINEARSVC EMOTION MODEL EVALUATION ===")
            print(f"Accuracy: {accuracy:.4f}")
            print("\nDetailed classification report:")
            print(classification_report(y_test, y_pred))

            # Return metrics
            return {
                "accuracy": round(accuracy * 100, 2),
                "samples": len(X_test),
                # "unique_emotions": sorted(y_test.unique())
            }
