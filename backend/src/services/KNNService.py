import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path
import joblib
import time

BASE_DIR = Path(__file__).resolve().parent                    # /app/src/services
MODELS_DIR = (BASE_DIR / '..' / 'AIModels').resolve()         # /app/src/AIModels
DATASET_DIR = (BASE_DIR / '..' / 'dataset').resolve()         # /app/src/dataset
MODEL_PATH = (MODELS_DIR / 'emotion_naivebayes_model.pkl').resolve()

TRAIN_DATASET_PATH = (DATASET_DIR / 'train_dataset.csv').resolve()
TEST_DATASET_PATH = (DATASET_DIR / 'test_dataset.csv').resolve()

MODEL_FILE = os.path.join(MODELS_DIR, "emotion_knn_model.pkl")


class KNNService:
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
                print(f"⚠️ Failed to load saved KNN model ({e}), retraining model...")
                self.train_models()
        else:
            print("⚠️ No existing KNN model found, training a new one...")
            self.train_models()

    def train_models(self):
        """Train KNN model for emotion recognition"""
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
            ("vect", CountVectorizer(token_pattern=r'[^,]+', lowercase=False)),
            ("clf", KNeighborsClassifier(n_neighbors=5, weights='distance', metric='minkowski'))
        ])

        print("Training KNN emotion model...")
        start_time = time.time()
        self._emotion_model.fit(X_train, y_train)
        print(f"✅ KNN model trained in {time.time() - start_time:.2f} seconds")

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
        print(f"\n=== KNN EMOTION MODEL EVALUATION ===")
        print(f"Accuracy: {acc:.4f}")
        print("\nDetailed report:")
        print(classification_report(y_test, y_pred))

        return {
            "emotion_accuracy": acc,
            "emotion_predictions": y_pred
        }

    def predict(self, forteclass_sequence: str) -> str:
        """Predict emotion based on forteclass sequence"""
        if not forteclass_sequence or len(forteclass_sequence.strip()) == 0:
            raise ValueError("Invalid or empty forteclass sequence")

        if self._emotion_model is None:
            raise ValueError("Model has not been trained or loaded")

        return self._emotion_model.predict([forteclass_sequence])[0]

    def save_model(self):
        """Save the trained model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self._emotion_model, self.model_path)
        print(f"💾 Model saved at: {self.model_path}")

    def load_model(self):
        """Load a previously saved model"""
        self._emotion_model = joblib.load(self.model_path)
        print(f"✅ KNN model successfully loaded from: {self.model_path}")
        
    def evaluate(self) -> dict:
            """
            Evaluates the trained KNN model on the test dataset.
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

            print(f"\n=== KNN EMOTION MODEL EVALUATION ===")
            print(f"Accuracy: {accuracy:.4f}")
            print("\nDetailed classification report:")
            print(classification_report(y_test, y_pred))

            # Return metrics
            return {
                "accuracy": round(accuracy * 100, 2),
                "samples": len(X_test),
                # "unique_emotions": sorted(y_test.unique())
            }
