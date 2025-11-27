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
MODELS_DIR = (BASE_DIR / '..' / 'final-models').resolve()
DATASET_DIR = (BASE_DIR / '..' / 'final-dataset').resolve()

RAW_DATASET_PATH = os.path.join(DATASET_DIR, 'raw_dataset.csv')  

CHUNKED_DATASET_PATH = os.path.join(DATASET_DIR, 'chunked_dataset.csv')  

BALANCED_CHUNKED_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_chunked_40_strict_dataset.csv')  
CHUNKED_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'chunked_40_strict_train_dataset.csv')
CHUNKED_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'chunked_40_strict_test_dataset.csv')
BALANCED_CHUNKED_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_chunked_40_strict_train_dataset.csv')
BALANCED_CHUNKED_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'balanced_chunked_40_strict_test_dataset.csv')
RF_BALANCED_CHUNKED_PATH = os.path.join(MODELS_DIR, 'random_forest_balanced_chunked_40_strict_model.pkl')

class ModelTrainingService:
    def build_chunked_dataset(self, chunk_size=40) -> str:
        if not os.path.exists(RAW_DATASET_PATH):
            raise FileNotFoundError(f"Raw dataset not found: {RAW_DATASET_PATH}")

        df = pd.read_csv(RAW_DATASET_PATH)

        if "num_classes" not in df.columns:
            raise ValueError("raw_dataset.csv must contain a num_classes column.")

        print(f"📊 Loaded RAW dataset: {df.shape[0]} samples")

        new_rows = []

        for idx, row in df.iterrows():
            full_seq = row["forteclass_sequence"]
            emotion = row["emotion"]
            mode = row["mode"]

            tokens = [t for t in full_seq.split(",") if t.strip()]

            # Skip rows that are smaller than chunk_size (cannot produce any valid chunk)
            if len(tokens) < chunk_size:
                continue

            # Split into perfect chunks of 50
            for i in range(0, len(tokens), chunk_size):
                sub = tokens[i:i + chunk_size]

                # Only accept perfect chunks
                if len(sub) == chunk_size:
                    new_rows.append({
                        "forteclass_sequence": ",".join(sub),
                        "num_classes": chunk_size,
                        "mode": mode,
                        "emotion": emotion
                    })

        # Convert to dataframe
        out_df = pd.DataFrame(new_rows)

        out_df.to_csv(CHUNKED_DATASET_PATH, index=False)

        print(f"\n✅ Chunking complete!")
        print(f"📄 New dataset saved: {CHUNKED_DATASET_PATH}")
        print(f"🆕 Total rows: {out_df.shape[0]} (was {df.shape[0]})")
        print(f"📉 Average num_classes AFTER chunking: {out_df['num_classes'].mean():.2f}")

        return CHUNKED_DATASET_PATH

    def build_balanced_chunked_dataset(self) -> str:
        if not os.path.exists(CHUNKED_DATASET_PATH):
            raise FileNotFoundError(f"chunked_dataset not found: {CHUNKED_DATASET_PATH}")

        df = pd.read_csv(CHUNKED_DATASET_PATH)

        if "emotion" not in df.columns:
            raise ValueError("Dataset must contain an 'emotion' column.")

        print(f"📄 Loaded CHUNKED_50 dataset: {df.shape[0]} samples")

        counts = df["emotion"].value_counts()
        min_size = counts.min()

        print("\n📊 Distribution BEFORE balancing:")
        for e, c in counts.items():
            print(f"   • {e}: {c}")

        print(f"\n➡️ Balancing using minority class size: {min_size}")

        balanced_parts = []
        for emotion in counts.index:
            part = df[df["emotion"] == emotion].sample(
                n=min_size,
                replace=False,
                random_state=42
            )
            balanced_parts.append(part)

        balanced_df = pd.concat(balanced_parts, ignore_index=True)
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

        os.makedirs(os.path.dirname(BALANCED_CHUNKED_DATASET_PATH), exist_ok=True)
        balanced_df.to_csv(BALANCED_CHUNKED_DATASET_PATH, index=False)

        print("\n✅ Balanced dataset created!")
        print(f"📄 Saved: {BALANCED_CHUNKED_DATASET_PATH}")
        print("\n📊 Distribution AFTER balancing:")
        for e, c in balanced_df["emotion"].value_counts().items():
            print(f"   • {e}: {c}")

        return BALANCED_CHUNKED_DATASET_PATH
    
    def build_balanced_chunked_dataset_traintest(self) -> str:
        if not os.path.exists(CHUNKED_TEST_DATASET_PATH):
            raise FileNotFoundError(f"test_chunked_dataset not found: {CHUNKED_TEST_DATASET_PATH}")
        
        if not os.path.exists(CHUNKED_TRAIN_DATASET_PATH):
            raise FileNotFoundError(f"train_chunked_dataset not found: {CHUNKED_TRAIN_DATASET_PATH}")

        dfTrain = pd.read_csv(CHUNKED_TRAIN_DATASET_PATH)
        dfTest = pd.read_csv(CHUNKED_TEST_DATASET_PATH)


        if "emotion" not in dfTrain.columns:
            raise ValueError("Dataset must contain an 'emotion' column.")
        
        if "emotion" not in dfTest.columns:
            raise ValueError("Dataset must contain an 'emotion' column.")

        # TRAIN
        print(f"📄 Loaded CHUNKED_50 dataset: {dfTrain.shape[0]} samples")

        counts = dfTrain["emotion"].value_counts()
        min_size = counts.min()

        print("\n📊 Distribution BEFORE balancing:")
        for e, c in counts.items():
            print(f"   • {e}: {c}")

        print(f"\n➡️ Balancing using minority class size: {min_size}")

        balanced_parts = []
        for emotion in counts.index:
            part = dfTrain[dfTrain["emotion"] == emotion].sample(
                n=min_size,
                replace=False,
                random_state=42
            )
            balanced_parts.append(part)

        balanced_dfTrain = pd.concat(balanced_parts, ignore_index=True)
        balanced_dfTrain = balanced_dfTrain.sample(frac=1, random_state=42).reset_index(drop=True)

        os.makedirs(os.path.dirname(BALANCED_CHUNKED_TRAIN_DATASET_PATH), exist_ok=True)
        balanced_dfTrain.to_csv(BALANCED_CHUNKED_TRAIN_DATASET_PATH, index=False)

        print("\n✅ Balanced TRAIN dataset created!")
        print(f"📄 Saved: {BALANCED_CHUNKED_TRAIN_DATASET_PATH}")


        # TEST
        print(f"📄 Loaded CHUNKED_50 dataset: {dfTest.shape[0]} samples")

        counts = dfTest["emotion"].value_counts()
        min_size = counts.min()

        print("\n📊 Distribution BEFORE balancing:")
        for e, c in counts.items():
            print(f"   • {e}: {c}")

        print(f"\n➡️ Balancing using minority class size: {min_size}")

        balanced_parts = []
        for emotion in counts.index:
            part = dfTest[dfTest["emotion"] == emotion].sample(
                n=min_size,
                replace=False,
                random_state=42
            )
            balanced_parts.append(part)

        balanced_dfTest = pd.concat(balanced_parts, ignore_index=True)
        balanced_dfTest = balanced_dfTest.sample(frac=1, random_state=42).reset_index(drop=True)

        os.makedirs(os.path.dirname(BALANCED_CHUNKED_TEST_DATASET_PATH), exist_ok=True)
        balanced_dfTest.to_csv(BALANCED_CHUNKED_TEST_DATASET_PATH, index=False)

        print("\n✅ Balanced TRAIN dataset created!")
        print(f"📄 Saved: {BALANCED_CHUNKED_TEST_DATASET_PATH}")
 

        return BALANCED_CHUNKED_TRAIN_DATASET_PATH, BALANCED_CHUNKED_TEST_DATASET_PATH

    def split_balanced_dataset(self, test_ratio=0.20):
        if not os.path.exists(BALANCED_CHUNKED_DATASET_PATH):
            raise FileNotFoundError(f"Balanced chunked dataset missing: {BALANCED_CHUNKED_DATASET_PATH}")

        df = pd.read_csv(BALANCED_CHUNKED_DATASET_PATH)

        print(f"📄 Loaded balanced dataset: {df.shape[0]} samples")

        test_df = df.sample(frac=test_ratio, random_state=42)
        train_df = df.drop(test_df.index)

        os.makedirs(os.path.dirname(CHUNKED_TRAIN_DATASET_PATH), exist_ok=True)

        train_df.to_csv(CHUNKED_TRAIN_DATASET_PATH, index=False)
        test_df.to_csv(CHUNKED_TEST_DATASET_PATH, index=False)

        print("\n✅ Balanced dataset split!")
        print(f"📄 Train: {CHUNKED_TRAIN_DATASET_PATH} ({train_df.shape[0]} samples)")
        print(f"📄 Test:  {CHUNKED_TEST_DATASET_PATH} ({test_df.shape[0]} samples)")

        return CHUNKED_TRAIN_DATASET_PATH, CHUNKED_TEST_DATASET_PATH
    
    def train_balanced_dataset(self):
        if not os.path.exists(BALANCED_CHUNKED_TRAIN_DATASET_PATH):
            raise FileNotFoundError(f"Train dataset not found: {BALANCED_CHUNKED_TRAIN_DATASET_PATH}")

        df = pd.read_csv(BALANCED_CHUNKED_TRAIN_DATASET_PATH)
        df = df.dropna(subset=['forteclass_sequence', 'mode', 'emotion'])
        df = df[df['forteclass_sequence'].str.len() > 0]

        if len(df) == 0:
            raise ValueError("No usable rows found in the train dataset after cleaning.")

        X = (df['forteclass_sequence'] + " | " + df['mode']).astype(str).values
        y = df['emotion'].astype(str).values

        print(f"📚 Training on {len(X)} samples (ALL train dataset) ...")

        pipeline = Pipeline([
            ("vect", CountVectorizer(
                lowercase=False,
                token_pattern=r"[0-9A-Za-z\-]+",
                ngram_range=(1, 5),
                max_features=24000
            )),
            ("lda", LatentDirichletAllocation(
                n_components=30,
                max_iter=40,
                learning_method="online",
                learning_decay=0.7,
                n_jobs=-1,
                random_state=42
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

        print("🔧 Fitting pipeline (vectorizer -> LDA -> RandomForest)...")
        pipeline.fit(X, y)
        print("✅ Training complete.")

        # ✅ SAVE ALL COMPONENTS (vect + lda + clf)
        package = {
            "vectorizer": pipeline.named_steps["vect"],
            "lda": pipeline.named_steps["lda"],
            "model": pipeline.named_steps["clf"]
        }

        os.makedirs(os.path.dirname(RF_BALANCED_CHUNKED_PATH), exist_ok=True)
        joblib.dump(package, RF_BALANCED_CHUNKED_PATH, compress=3)

        print(f"💾 Balanced model package saved at: {RF_BALANCED_CHUNKED_PATH}")

