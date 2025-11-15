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

CHUNK_DATASET_PATH = os.path.join(DATASET_DIR, 'chunked_dataset.csv')  
CHUNK_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'chunk_train_dataset.csv')
CHUNK_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'chunk_test_dataset.csv')
RF_CHUNKED_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_chunked_v1.pkl')

class AITrainingService:

    def __init__(self, action: str = None):
        self.rf_model_path = os.path.abspath(RF_MODEL_PATH)

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
            n_estimators=200,
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
    
    # -------------------------------------------------------------
    # CHUNK DATASET BASED ON FORTECLASS AVERAGE
    # -------------------------------------------------------------
    def chunk_dataset_based_on_forteclasses_average(self, min_chunk=12, max_chunk=20) -> str:
        if not os.path.exists(RAW_DATASET_PATH):
            raise FileNotFoundError(f"Raw dataset not found: {RAW_DATASET_PATH}")

        df = pd.read_csv(RAW_DATASET_PATH)

        if "num_classes" not in df.columns:
            raise ValueError("raw_dataset.csv must contain a num_classes column.")

        print(f"📊 Loaded RAW dataset: {df.shape[0]} samples")
        print("🔍 Analyzing num_classes distribution...")

        min_val = df["num_classes"].min()
        max_val = df["num_classes"].max()
        avg_val = df["num_classes"].mean()
        median_val = df["num_classes"].median()

        print(f"   ➤ Min: {min_val}")
        print(f"   ➤ Max: {max_val}")
        print(f"   ➤ Avg: {avg_val:.2f}")
        print(f"   ➤ Median: {median_val}")

        # -------------------------------------------------
        # Determine chunk size
        # -------------------------------------------------
        # Logic:
        # If average progression is too long (>60), chunk = ~15
        # If moderately long (>40), chunk = ~18
        # Otherwise use median in range [min_chunk, max_chunk]

        if avg_val > 60:
            chunk_size = 15
        elif avg_val > 40:
            chunk_size = 18
        else:
            chunk_size = int(max(min(avg_val // 1, max_chunk), min_chunk))

        print(f"\n📐 Using chunk_size = {chunk_size}")

        new_rows = []

        # -------------------------------------------------
        # Walk through the dataset row by row
        # -------------------------------------------------
        for idx, row in df.iterrows():
            full_seq = row["forteclass_sequence"]
            emotion = row["emotion"]
            mode = row["mode"]

            # Split forteclass string into list
            tokens = [t for t in full_seq.split(",") if t.strip() != ""]

            # If small, keep row unchanged
            if len(tokens) <= chunk_size:
                new_rows.append({
                    "forteclass_sequence": ",".join(tokens),
                    "num_classes": len(tokens),
                    "mode": mode,
                    "emotion": emotion
                })
                continue

            # If long → split into chunks
            for i in range(0, len(tokens), chunk_size):
                sub = tokens[i:i + chunk_size]
                if len(sub) == 0:
                    continue

                new_rows.append({
                    "forteclass_sequence": ",".join(sub),
                    "num_classes": len(sub),
                    "mode": mode,
                    "emotion": emotion
                })

        # Convert to dataframe
        out_df = pd.DataFrame(new_rows)

        CHUNKED_PATH = os.path.join(DATASET_DIR, "chunked_dataset.csv")
        out_df.to_csv(CHUNKED_PATH, index=False)

        print(f"\n✅ Chunking complete!")
        print(f"📄 New dataset saved: {CHUNKED_PATH}")
        print(f"🆕 Total rows: {out_df.shape[0]} (was {df.shape[0]})")
        print(f"📉 Average num_classes AFTER chunking: {out_df['num_classes'].mean():.2f}")

        return CHUNKED_PATH
    
    # -------------------------------------------------------------
    # SPLIT CHUNK DATASET
    # -------------------------------------------------------------
    def split_chunk_dataset(self, test_size=0.2, random_state=42) -> dict:
        if not os.path.exists(CHUNK_DATASET_PATH):
            raise FileNotFoundError(f"Chunk dataset not found: {CHUNK_DATASET_PATH}")

        df = pd.read_csv(CHUNK_DATASET_PATH)

        print(f"📊 Loaded CHUNK dataset: {df.shape[0]} samples")
        print(f"📤 Splitting into train/test ({int((1 - test_size) * 100)}% / {int(test_size * 100)}%)")

        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df["emotion"]
        )

        train_df.to_csv(CHUNK_TRAIN_DATASET_PATH, index=False)
        test_df.to_csv(CHUNK_TEST_DATASET_PATH, index=False)

        print(f"✅ Train dataset saved: {CHUNK_TRAIN_DATASET_PATH} ({train_df.shape[0]} samples)")
        print(f"🧪 Test dataset saved:  {CHUNK_TEST_DATASET_PATH} ({test_df.shape[0]} samples)")

        return {
            "train_samples": train_df.shape[0],
            "test_samples": test_df.shape[0]
        }
    
    # -------------------------------------------------------------
    # TRAIN CHUNKED MODEL
    # -------------------------------------------------------------
    def train_chunk_model(self):
        if not os.path.exists(CHUNK_TRAIN_DATASET_PATH):
            raise FileNotFoundError(
                f"Chunked train dataset missing: {CHUNK_TRAIN_DATASET_PATH}\n"
                f"➡️ Run split_chunk_dataset() first."
            )

        train_df = pd.read_csv(CHUNK_TRAIN_DATASET_PATH)

        print(f"📚 Training CHUNKED model with {train_df.shape[0]} samples...")

        # ---------- FEATURES ----------
        X = train_df["forteclass_sequence"] + " | " + train_df["mode"]
        y = train_df["emotion"]

        print("🔧 Building CHUNKED pipeline (CountVectorizer + RandomForest)...")

        vectorizer = CountVectorizer(
            analyzer="word",
            ngram_range=(1, 4),
            token_pattern=r"[^, ]+"
        )

        # ~50%
        rf = RandomForestClassifier(
            max_depth=30,
            n_estimators=1000,
            min_samples_leaf=2,
            min_samples_split=4,
            n_jobs=-1,
            max_features="sqrt",
        )
 
        pipeline = Pipeline([
            ("vect", vectorizer),
            ("clf", rf)
        ])

        print("🚀 Training CHUNKED model...")
        pipeline.fit(X, y)
        print("✅ Chunked training complete!")

        # Prepare saving
        package = {
            "vectorizer": pipeline.named_steps["vect"],
            "model": pipeline.named_steps["clf"]
        }

        os.makedirs(os.path.dirname(RF_CHUNKED_MODEL_PATH), exist_ok=True)

        joblib.dump(package, RF_CHUNKED_MODEL_PATH, compress=3)

        print(f"💾 CHUNKED model saved in: {RF_CHUNKED_MODEL_PATH}")

        # Keep in memory
        self._chunk_emotion_model = pipeline

