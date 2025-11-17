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
                token_pattern=r"[0-9A-Za-z\-]+",
                ngram_range=(1, 5),
                max_features=24000
            )),
            ("lda", LatentDirichletAllocation(
                n_components = 30,
                max_iter = 40,
                learning_method = "online",
                learning_decay = 0.7,
                n_jobs=-1
            )),
            ("clf", RandomForestClassifier(
                n_estimators=1200,
                max_depth=25,
                min_samples_leaf=2,
                min_samples_split=4,
                max_features="log2",
                n_jobs=-1,
                random_state=42
            ))
            # ("vect", CountVectorizer(
            #     lowercase=False,
            #     token_pattern="[^, ]+",
            #     ngram_range=(1, 4),
            #     max_features=12000
            # )),
            # ("lda", LatentDirichletAllocation(
            #     n_components=12,
            #     max_iter=20,
            #     learning_method="batch",
            #     n_jobs=-1,
            #     random_state=42
            # )),
            # ("clf", RandomForestClassifier(
            #     n_estimators=800,
            #     max_depth=30,
            #     min_samples_leaf=2,
            #     min_samples_split=4,
            #     n_jobs=-1,
            #     max_features="sqrt",
            #     random_state=42
            # ))
        ])

        print("🏋️ Training model (vectorizer → LDA → RF)...")
        pipeline.fit(X, y)

        print("💾 Saving FULL pipeline...")
        joblib.dump(pipeline, RF_NGRAMS_MODEL_PATH)

        print(f"✅ Training complete. Saved pipeline to:\n{RF_NGRAMS_MODEL_PATH}")

    def build_full_ngrams_dataset(self) -> str:
        if not os.path.exists(RAW_DATASET_PATH):
            raise FileNotFoundError(
                f"Chunk dataset missing: {RAW_DATASET_PATH}\n"
                f"➡️ Run chunk_dataset_based_on_forteclasses_average() first."
            )

        df = pd.read_csv(RAW_DATASET_PATH)

        print(f"📊 Building FULL N-GRAMS dataset from {df.shape[0]} samples...")

        # Build the combined token sequence
        df["ngrams_input"] = df["forteclass_sequence"] + " | " + df["mode"]

        # Save
        df.to_csv(FULL_NGRAMS_DATASET_PATH, index=False)

        print(f"✅ N-GRAMS dataset saved: {FULL_NGRAMS_DATASET_PATH}")

        return FULL_NGRAMS_DATASET_PATH
    
    def split_full_ngrams_dataset(self, test_size=0.15, random_state=42) -> dict:
        if not os.path.exists(FULL_NGRAMS_DATASET_PATH):
            raise FileNotFoundError(
                f"N-grams dataset missing: {FULL_NGRAMS_DATASET_PATH}\n"
                f"➡️ Run build_full_ngrams_dataset() first."
            )

        df = pd.read_csv(FULL_NGRAMS_DATASET_PATH)

        print(f"📊 Loaded FULL N-GRAMS dataset: {df.shape[0]} samples")
        print(f"📤 Splitting ({100 - int(test_size*100)}% train / {int(test_size*100)}% test)")

        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df["emotion"]
        )

        train_df.to_csv(FULL_NGRAMS_TRAIN_DATASET_PATH, index=False)
        test_df.to_csv(FULL_NGRAMS_TEST_DATASET_PATH, index=False)

        print(f"✅ FULL N-GRAMS train saved: {FULL_NGRAMS_TRAIN_DATASET_PATH} ({train_df.shape[0]} samples)")
        print(f"🧪 FULL N-GRAMS test saved:  {FULL_NGRAMS_TEST_DATASET_PATH} ({test_df.shape[0]} samples)")

        return {
            "train_samples": train_df.shape[0],
            "test_samples": test_df.shape[0]
        }
    
    def train_full_ngrams_model(self):
        print("📘 Loading dataset...")
        df = pd.read_csv(FULL_NGRAMS_TRAIN_DATASET_PATH)
        df = df.dropna(subset=["ngrams_input", "emotion"])

        X = df["ngrams_input"].astype(str)
        y = df["emotion"].astype(str)

        print("🔧 Building pipeline...")

        pipeline = Pipeline([
            ("vect", CountVectorizer(
                lowercase=False,
                token_pattern=r"[0-9A-Za-z\-]+",
                ngram_range=(1, 5),
                max_features=24000
            )),
            ("lda", LatentDirichletAllocation(
                n_components = 30,
                max_iter = 40,
                learning_method = "online",
                learning_decay = 0.7,
                n_jobs=-1
            )),
            ("clf", RandomForestClassifier(
                n_estimators=1200,
                max_depth=25,
                min_samples_leaf=2,
                min_samples_split=4,
                max_features="log2",
                n_jobs=-1,
                random_state=42
            ))
        ])

        print("🏋️ Training model (vectorizer → LDA → RF)...")
        pipeline.fit(X, y)

        print("💾 Saving FULL pipeline...")
        joblib.dump(pipeline, RF_FULL_NGRAMS_MODEL_PATH)

        print(f"✅ Training complete. Saved pipeline to:\n{RF_FULL_NGRAMS_MODEL_PATH}")

    def create_balanced_chunk_dataset(self) -> str:
        if not os.path.exists(CHUNK_DATASET_PATH):
            raise FileNotFoundError(f"Chunk dataset not found: {CHUNK_DATASET_PATH}")

        df = pd.read_csv(CHUNK_DATASET_PATH)

        print(f"📊 Loaded CHUNK dataset: {df.shape[0]} samples")
        print("🔍 Counting emotion frequencies...")

        counts = df["emotion"].value_counts()
        print(counts)

        min_count = counts.min()
        print(f"\n🔎 Minimum class size detected = {min_count}")

        print("✂️ Undersampling all classes to minimum count...")

        balanced_parts = []

        for emotion, emotion_df in df.groupby("emotion"):
            sampled = emotion_df.sample(
                n=min_count,
                replace=False,
                random_state=42
            )
            balanced_parts.append(sampled)

        balanced_df = pd.concat(balanced_parts, axis=0).sample(frac=1, random_state=42)

        balanced_df.to_csv(BALANCED_CHUNK_DATASET_PATH, index=False)

        print(f"\n✅ Balanced dataset created!")
        print(f"📄 Saved at: {BALANCED_CHUNK_DATASET_PATH}")
        print(f"🆕 Total rows: {balanced_df.shape[0]} (each class = {min_count})")

        return BALANCED_CHUNK_DATASET_PATH
    
    def split_balanced_chunk_dataset(self, test_size=0.2, random_state=42) -> dict:
        if not os.path.exists(BALANCED_CHUNK_DATASET_PATH):
            raise FileNotFoundError(f"Balanced chunk dataset not found: {BALANCED_CHUNK_DATASET_PATH}")

        df = pd.read_csv(BALANCED_CHUNK_DATASET_PATH)

        print(f"📊 Loaded BALANCED dataset: {df.shape[0]} samples")
        print(f"📤 Splitting into train/test ({100 - int(test_size*100)}% / {int(test_size*100)}%)")

        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df["emotion"]
        )

        train_df.to_csv(BALANCED_CHUNK_TRAIN_DATASET_PATH, index=False)
        test_df.to_csv(BALANCED_CHUNK_TEST_DATASET_PATH, index=False)

        print(f"✅ Balanced TRAIN saved: {BALANCED_CHUNK_TRAIN_DATASET_PATH} ({train_df.shape[0]} samples)")
        print(f"🧪 Balanced TEST saved:  {BALANCED_CHUNK_TEST_DATASET_PATH} ({test_df.shape[0]} samples)")

        return {
            "train_samples": train_df.shape[0],
            "test_samples": test_df.shape[0]
        }
    
    def train_balanced_chunk_model(self):
        if not os.path.exists(BALANCED_CHUNK_TRAIN_DATASET_PATH):
            raise FileNotFoundError(
                f"Balanced chunk train dataset missing: {BALANCED_CHUNK_TRAIN_DATASET_PATH}\n"
                f"➡️ Run split_balanced_chunk_dataset() first."
            )

        df = pd.read_csv(BALANCED_CHUNK_TRAIN_DATASET_PATH)

        print(f"📚 Training BALANCED CHUNK model with {df.shape[0]} samples...")

        X = df["forteclass_sequence"] + " | " + df["mode"]
        y = df["emotion"]

        vectorizer = CountVectorizer(
            analyzer="word",
            ngram_range=(1, 4),
            token_pattern=r"[^, ]+"
        )

        rf = RandomForestClassifier(
            n_estimators=1000,
            max_depth=30,
            min_samples_leaf=2,
            min_samples_split=4,
            max_features="sqrt",
            n_jobs=-1,
            random_state=42
        )

        pipeline = Pipeline([
            ("vect", vectorizer),
            ("clf", rf)
        ])

        print("🚀 Training BALANCED model...")
        pipeline.fit(X, y)

        package = {
            "vectorizer": pipeline.named_steps["vect"],
            "model": pipeline.named_steps["clf"]
        }

        joblib.dump(package, RF_BALANCED_CHUNK_MODEL_PATH, compress=3)

        print(f"💾 Balanced model saved at: {RF_BALANCED_CHUNK_MODEL_PATH}")

        self._balanced_chunk_model = pipeline

    def create_balanced_dataset_ngrams_lda(self):
        if not os.path.exists(BALANCED_CHUNK_DATASET_PATH):
            raise FileNotFoundError(f"Raw dataset not found: {BALANCED_CHUNK_DATASET_PATH}")

        df = pd.read_csv(BALANCED_CHUNK_DATASET_PATH)
        df = df.dropna(subset=["forteclass_sequence", "emotion", "mode"])
        df = df[df["forteclass_sequence"].str.len() > 0]

        # Ensure balanced dataset
        min_count = df["emotion"].value_counts().min()
        df_balanced = (
            df.groupby("emotion")
            .sample(n=min_count, random_state=42)
            .reset_index(drop=True)
        )

        # Create ngrams_input = sequence | mode
        df_balanced["ngrams_input"] = (
            df_balanced["forteclass_sequence"] + " | " + df_balanced["mode"]
        )

        df_balanced.to_csv(BALANCED_NGRAMS_DATASET_PATH, index=False)

        print("✅ Balanced dataset for NGRAMS + LDA generated!")
        print(df_balanced["emotion"].value_counts())
        return df_balanced
    
    def split_balanced_dataset_ngrams_lda(self, test_size=0.20):
        if not os.path.exists(BALANCED_NGRAMS_DATASET_PATH):
            raise FileNotFoundError(f"Balanced dataset missing: {BALANCED_NGRAMS_DATASET_PATH}")

        df = pd.read_csv(BALANCED_NGRAMS_DATASET_PATH)

        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            stratify=df["emotion"],
            random_state=42
        )

        train_df.to_csv(BALANCED_NGRAMS_TRAIN_DATASET_PATH, index=False)
        test_df.to_csv(BALANCED_NGRAMS_TEST_DATASET_PATH, index=False)

        print("📌 Balanced NGRAMS+LDA train/test split done!")
        print("Train size:", len(train_df), " Test size:", len(test_df))

        return train_df, test_df
    
    def train_model_ngrams_lda_balanced(self):
        if not os.path.exists(BALANCED_NGRAMS_TRAIN_DATASET_PATH):
            raise FileNotFoundError("Dataset missing. Run create_balanced_dataset_ngrams_lda().")

        df = pd.read_csv(BALANCED_NGRAMS_TRAIN_DATASET_PATH)

        X = df["ngrams_input"].astype(str).tolist()
        y = df["emotion"].astype(str).tolist()

        pipeline = Pipeline([
            ("vect", CountVectorizer(
                lowercase=False,
                token_pattern=r"[^, ]+",
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
                n_estimators=800,
                max_depth=30,
                min_samples_leaf=2,
                min_samples_split=4,
                n_jobs=-1,
                max_features="sqrt",
                random_state=42
            ))
        ])

        print("🔄 Training NGRAMS + LDA + RandomForest (balanced)...")
        pipeline.fit(X, y)

        joblib.dump(pipeline, RF_BALANCED_NGRAMS_MODEL_PATH)
        print(f"✅ Model saved → {RF_BALANCED_NGRAMS_MODEL_PATH}")

        return pipeline


