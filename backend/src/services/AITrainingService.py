import os
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import TruncatedSVD, LatentDirichletAllocation
from sklearn.pipeline import FeatureUnion
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

NGRAMS_DATASET_PATH = os.path.join(DATASET_DIR, 'ngrams_dataset.csv')
NGRAMS_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'ngrams_train_dataset.csv')
NGRAMS_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'ngrams_test_dataset.csv')
RF_NGRAMS_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_ngrams_v1.pkl')

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

    def build_ngrams_dataset(self) -> str:
        """
        Uses the chunked dataset to build the N-grams/LDA-ready dataset.
        Basically just copies chunked_dataset.csv into a new file but prepares the
        sequence string in the correct format.
        """
        if not os.path.exists(CHUNK_DATASET_PATH):
            raise FileNotFoundError(
                f"Chunk dataset missing: {CHUNK_DATASET_PATH}\n"
                f"➡️ Run chunk_dataset_based_on_forteclasses_average() first."
            )

        df = pd.read_csv(CHUNK_DATASET_PATH)

        print(f"📊 Building N-GRAMS dataset from {df.shape[0]} chunked samples...")

        # Build the combined token sequence
        df["ngrams_input"] = df["forteclass_sequence"] + " | " + df["mode"]

        # Save
        df.to_csv(NGRAMS_DATASET_PATH, index=False)

        print(f"✅ N-GRAMS dataset saved: {NGRAMS_DATASET_PATH}")

        return NGRAMS_DATASET_PATH
    
    def split_ngrams_dataset(self, test_size=0.2, random_state=42) -> dict:
        if not os.path.exists(NGRAMS_DATASET_PATH):
            raise FileNotFoundError(
                f"N-grams dataset missing: {NGRAMS_DATASET_PATH}\n"
                f"➡️ Run build_ngrams_dataset() first."
            )

        df = pd.read_csv(NGRAMS_DATASET_PATH)

        print(f"📊 Loaded N-GRAMS dataset: {df.shape[0]} samples")
        print(f"📤 Splitting ({100 - int(test_size*100)}% train / {int(test_size*100)}% test)")

        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df["emotion"]
        )

        train_df.to_csv(NGRAMS_TRAIN_DATASET_PATH, index=False)
        test_df.to_csv(NGRAMS_TEST_DATASET_PATH, index=False)

        print(f"✅ N-GRAMS train saved: {NGRAMS_TRAIN_DATASET_PATH} ({train_df.shape[0]} samples)")
        print(f"🧪 N-GRAMS test saved:  {NGRAMS_TEST_DATASET_PATH} ({test_df.shape[0]} samples)")

        return {
            "train_samples": train_df.shape[0],
            "test_samples": test_df.shape[0]
        }
    
    # def train_ngrams_model(self):
    #     """
    #     Train the Random Forest using N-grams + SVD + LDA features.
    #     Saves model into RF_NGRAMS_MODEL_PATH.
    #     """
    #     if not os.path.exists(NGRAMS_TRAIN_DATASET_PATH):
    #         raise FileNotFoundError(
    #             f"N-grams train dataset missing: {NGRAMS_TRAIN_DATASET_PATH}\n"
    #             f"➡️ Run split_ngrams_dataset() first."
    #         )

    #     df = pd.read_csv(NGRAMS_TRAIN_DATASET_PATH)

    #     print(f"📚 Training N-GRAMS model with {df.shape[0]} samples...")

    #     X = df["ngrams_input"]
    #     y = df["emotion"]

    #     print("🔧 Building N-GRAMS pipeline (Vectorizer + SVD + LDA + RF)...")

    #     vectorizer = CountVectorizer(
    #         token_pattern=r"[^, ]+",
    #         ngram_range=(1, 4),
    #         lowercase=False,
    #         max_features=12000
    #     )

    #     svd = TruncatedSVD(
    #         n_components=150,
    #         random_state=42
    #     )

    #     lda = LatentDirichletAllocation(
    #         n_components=12,
    #         learning_method="batch",
    #         max_iter=20,
    #         random_state=42,
    #         n_jobs=-1
    #     )

    #     # Combined feature extraction
    #     features = FeatureUnion([
    #         ("svd", Pipeline([
    #             ("vect", vectorizer),
    #             ("svd", svd)
    #         ])),
    #         ("lda", Pipeline([
    #             ("vect", vectorizer),
    #             ("lda", lda)
    #         ]))
    #     ])

    #     # Final classifier
    #     rf = RandomForestClassifier(
    #         n_estimators=500,
    #         max_depth=25,
    #         min_samples_leaf=2,
    #         n_jobs=-1,
    #         class_weight="balanced",
    #         max_features="sqrt",
    #         random_state=42
    #     )

    #     # Full pipeline
    #     pipeline = Pipeline([
    #         ("features", features),
    #         ("clf", rf)
    #     ])

    #     print("🚀 Training N-GRAMS model...")
    #     pipeline.fit(X, y)
    #     print("✅ N-GRAMS model training complete!")

    #     # Save individual components for reload compatibility
    #     package = {
    #         "vectorizer": vectorizer,
    #         "svd": svd,
    #         "lda": lda,
    #         "model": rf
    #     }

    #     os.makedirs(os.path.dirname(RF_NGRAMS_MODEL_PATH), exist_ok=True)

    #     joblib.dump(package, RF_NGRAMS_MODEL_PATH, compress=3)

    #     print(f"💾 N-GRAMS model saved: {RF_NGRAMS_MODEL_PATH}")

    #     self._ngrams_emotion_model = pipeline

    def train_ngrams_model(self):
        print("📘 Loading dataset...")
        df = pd.read_csv(NGRAMS_TRAIN_DATASET_PATH)
        df = df.dropna(subset=["ngrams_input", "emotion"])

        X = df["ngrams_input"].astype(str)
        y = df["emotion"].astype(str)

        print("🔧 Building pipeline...")

        pipeline = Pipeline([
            ("vect", CountVectorizer(
                lowercase=False,
                token_pattern="[^, ]+",
                ngram_range=(1, 4),
                max_features=12000
            )),
            ("lda", LatentDirichletAllocation(
                n_components=12,
                max_iter=20,
                learning_method="batch",
                n_jobs=-1,
                random_state=42
            )),
            ("clf", RandomForestClassifier(
                n_estimators=500,
                max_depth=25,
                min_samples_leaf=2,
                class_weight="balanced",
                n_jobs=-1,
                random_state=42
            ))
        ])

        print("🏋️ Training model (vectorizer → LDA → RF)...")
        pipeline.fit(X, y)

        print("💾 Saving FULL pipeline...")
        joblib.dump(pipeline, RF_NGRAMS_MODEL_PATH)

        print(f"✅ Training complete. Saved pipeline to:\n{RF_NGRAMS_MODEL_PATH}")
