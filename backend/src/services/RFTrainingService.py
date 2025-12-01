import os
import pandas as pd
import numpy as np
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

FULL_DATASET_DATASET_PATH = os.path.join(DATASET_DIR, 'full_dataset.csv')  
FULL_DATASET_TRAIN_DATASET_PATH = os.path.join(DATASET_DIR, 'full_train_dataset.csv')
FULL_DATASET_TEST_DATASET_PATH = os.path.join(DATASET_DIR, 'full_test_dataset.csv')
RF_FULL_PATH = os.path.join(MODELS_DIR, 'random_forest_full_model.pkl')

SAD_MAJOR_WEIGHT = 1.1
SAD_MINOR_WEIGHT = 1.3
DEFAULT_WEIGHT = 1.0

class RFTrainingService:
    def build_full_dataset(self) -> str:
        if not os.path.exists(RAW_DATASET_PATH):
            raise FileNotFoundError(
                f"Full dataset missing: {RAW_DATASET_PATH}"
            )

        df = pd.read_csv(RAW_DATASET_PATH)

        print(f"📊 Building FULL N-GRAMS dataset from {df.shape[0]} samples...")

        # Build the combined token sequence
        df["ngrams_input"] = df["forteclass_sequence"] + " | " + df["mode"]

        # Save
        df.to_csv(FULL_DATASET_DATASET_PATH, index=False)

        print(f"✅ N-GRAMS dataset saved: {FULL_DATASET_DATASET_PATH}")

        return FULL_DATASET_DATASET_PATH
    
    def split_full_dataset(self, test_size=0.15, random_state=42) -> dict:
        if not os.path.exists(FULL_DATASET_DATASET_PATH):
            raise FileNotFoundError(
                f"N-grams dataset missing: {FULL_DATASET_DATASET_PATH}"
            )

        df = pd.read_csv(FULL_DATASET_DATASET_PATH)

        print(f"📊 Loaded FULL N-GRAMS dataset: {df.shape[0]} samples")
        print(f"📤 Splitting ({100 - int(test_size*100)}% train / {int(test_size*100)}% test)")

        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df["emotion"]
        )

        train_df.to_csv(FULL_DATASET_TRAIN_DATASET_PATH, index=False)
        test_df.to_csv(FULL_DATASET_TEST_DATASET_PATH, index=False)

        print(f"✅ FULL N-GRAMS train saved: {FULL_DATASET_TRAIN_DATASET_PATH} ({train_df.shape[0]} samples)")
        print(f"🧪 FULL N-GRAMS test saved:  {FULL_DATASET_TEST_DATASET_PATH} ({test_df.shape[0]} samples)")

        return {
            "train_samples": train_df.shape[0],
            "test_samples": test_df.shape[0]
        }
    
    def calculate_sample_weights(self, df: pd.DataFrame) -> np.ndarray:
        sample_weights = np.full(len(df), DEFAULT_WEIGHT, dtype=np.float32)
        
        sad_mask = df['emotion'] == 'sad'
        sad_major_mask = sad_mask & (df['mode'] == 'major')
        sad_minor_mask = sad_mask & (df['mode'] == 'minor')
        
        sample_weights[sad_major_mask] = SAD_MAJOR_WEIGHT
        sample_weights[sad_minor_mask] = SAD_MINOR_WEIGHT
        
        sad_major_count = sad_major_mask.sum()
        sad_minor_count = sad_minor_mask.sum()
        
        print(f"  📊 Weighting applied:")
        print(f"    SAD Major ({SAD_MAJOR_WEIGHT}x): {sad_major_count:,} samples")
        print(f"    SAD Minor ({SAD_MINOR_WEIGHT}x): {sad_minor_count:,} samples")
        print(f"    Outras ({DEFAULT_WEIGHT}x): {len(df) - sad_major_count - sad_minor_count:,} samples")
        print(f"    Mean weight: {sample_weights.mean():.4f}")
        
        return sample_weights


    def train_full_dataset(self):
        print("📘 Loading dataset...")
        df_train = pd.read_csv(FULL_DATASET_TRAIN_DATASET_PATH)
        df_train = df_train.dropna(subset=["ngrams_input", "emotion", "mode"])
        
        X_train = df_train["ngrams_input"].astype(str)
        y_train = df_train["emotion"].astype(str)

        w_train = self.calculate_sample_weights(df_train)

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

        pipeline.fit(X_train, y_train, clf__sample_weight=w_train) 
        
        print("💾 Saving FULL pipeline...")
        joblib.dump(pipeline, RF_FULL_PATH)

        print(f"✅ Training complete. Saved pipeline to:\n{RF_FULL_PATH}")