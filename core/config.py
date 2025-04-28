# core/config.py

import os

# Base core directory
CORE_DIR = os.path.dirname(os.path.abspath(__file__))

# Models directory inside core
MODELS_DIR = os.path.join(CORE_DIR, "models")

# Daily and Weekly model subfolders
DAILY_MODELS_DIR = os.path.join(MODELS_DIR, "daily")
WEEKLY_MODELS_DIR = os.path.join(MODELS_DIR, "weekly")

# Ensure directories exist
os.makedirs(DAILY_MODELS_DIR, exist_ok=True)
os.makedirs(WEEKLY_MODELS_DIR, exist_ok=True)

# Model filenames
DAILY_RANDOM_FOREST_MODEL_PATH = os.path.join(DAILY_MODELS_DIR, "randomforest.pkl")
WEEKLY_RANDOM_FOREST_MODEL_PATH = os.path.join(WEEKLY_MODELS_DIR, "randomforest.pkl")

# Thresholds
DEFAULT_DAILY_STRONG_MOVE_THRESHOLD = 1.0
DEFAULT_WEEKLY_STRONG_MOVE_THRESHOLD = 8.0

# Random Forest Parameters
RANDOM_FOREST_N_ESTIMATORS = 1000
RANDOM_FOREST_MAX_DEPTH = 8
RANDOM_FOREST_MIN_SAMPLES = 5
RANDOM_FOREST_CLASS_WEIGHT = "balanced"
RANDOM_SEED = 42

# LightGBM Parameters
LIGHTGBM_N_ESTIMATORS = 1000
LIGHTGBM_LEARNING_RATE = 0.01
LIGHTGBM_MAX_DEPTH = 6
LIGHTGBM_NUM_LEAVES = 31
LIGHTGBM_MIN_CHILD_WEIGHT = 3


# Classifier names
RANDOM_FOREST = "randomforest"
XGBOOST = "xgboost"
LIGHTGBM = "lightgbm"


def get_daily_model_path(classifier_name: str) -> str:
    return os.path.join(DAILY_MODELS_DIR, f"{classifier_name}.pkl")
