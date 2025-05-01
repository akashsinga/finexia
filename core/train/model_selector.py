# core/train/model_selector.py

import os
from sklearn.ensemble import RandomForestClassifier
from core.config import (
    DAILY_MODELS_DIR, RANDOM_FOREST, XGBOOST, LIGHTGBM,
    RANDOM_FOREST_N_ESTIMATORS, RANDOM_FOREST_MAX_DEPTH,
    RANDOM_FOREST_MIN_SAMPLES, RANDOM_FOREST_CLASS_WEIGHT,
    LIGHTGBM_N_ESTIMATORS, LIGHTGBM_LEARNING_RATE,
    LIGHTGBM_MAX_DEPTH, LIGHTGBM_MIN_CHILD_WEIGHT
)

def get_classifier(name: str, random_seed: int = 42, scale_pos_weight: float = 1.0):
    if name == RANDOM_FOREST:
        return RandomForestClassifier(n_estimators=RANDOM_FOREST_N_ESTIMATORS,max_depth=RANDOM_FOREST_MAX_DEPTH,min_samples_split=RANDOM_FOREST_MIN_SAMPLES,class_weight=RANDOM_FOREST_CLASS_WEIGHT,random_state=random_seed)
    elif name == XGBOOST:
        from xgboost import XGBClassifier
        return XGBClassifier(n_estimators=300,max_depth=6,learning_rate=0.05,min_child_weight=3,random_state=random_seed,verbosity=0,scale_pos_weight=scale_pos_weight)
    elif name == LIGHTGBM:
        from lightgbm import LGBMClassifier
        return LGBMClassifier(n_estimators=LIGHTGBM_N_ESTIMATORS,learning_rate=LIGHTGBM_LEARNING_RATE,max_depth=LIGHTGBM_MAX_DEPTH,min_child_weight=LIGHTGBM_MIN_CHILD_WEIGHT,random_state=random_seed,verbosity=-1,scale_pos_weight=scale_pos_weight)
    else:
        raise ValueError(f"Unsupported classifier: {name}")

def get_model_path(symbol: str, model_type: str) -> str:
    return os.path.join(DAILY_MODELS_DIR, f"{symbol}_{model_type}.pkl")
