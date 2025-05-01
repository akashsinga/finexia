# core/config.py

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
DEFAULT_DAILY_STRONG_MOVE_THRESHOLD = float(os.getenv("DAILY_STRONG_MOVE_THRESHOLD", "8.0"))
DEFAULT_WEEKLY_STRONG_MOVE_THRESHOLD = float(os.getenv("WEEKLY_STRONG_MOVE_THRESHOLD", "8.0"))
STRONG_MOVE_CONFIDENCE_THRESHOLD = float(os.getenv("STRONG_MOVE_CONFIDENCE_THRESHOLD", "0.5"))

# Random Forest Parameters
RANDOM_FOREST_N_ESTIMATORS = int(os.getenv("RF_N_ESTIMATORS", "1000"))
RANDOM_FOREST_MAX_DEPTH = int(os.getenv("RF_MAX_DEPTH", "8"))
RANDOM_FOREST_MIN_SAMPLES = int(os.getenv("RF_MIN_SAMPLES", "5"))
RANDOM_FOREST_CLASS_WEIGHT = os.getenv("RF_CLASS_WEIGHT", "balanced")
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# LightGBM Parameters
LIGHTGBM_N_ESTIMATORS = int(os.getenv("LGBM_N_ESTIMATORS", "1000"))
LIGHTGBM_LEARNING_RATE = float(os.getenv("LGBM_LEARNING_RATE", "0.01"))
LIGHTGBM_MAX_DEPTH = int(os.getenv("LGBM_MAX_DEPTH", "6"))
LIGHTGBM_NUM_LEAVES = int(os.getenv("LGBM_NUM_LEAVES", "31"))
LIGHTGBM_MIN_CHILD_WEIGHT = int(os.getenv("LGBM_MIN_CHILD_WEIGHT", "3"))

# Classifier names
RANDOM_FOREST = "randomforest"
XGBOOST = "xgboost"
LIGHTGBM = "lightgbm"

# Cache configuration
MODEL_CACHE_SIZE = int(os.getenv("MODEL_CACHE_SIZE", "100"))  # Number of models to keep in memory
FEATURE_CACHE_ENABLED = os.getenv("FEATURE_CACHE_ENABLED", "True").lower() == "true"

def validate_config() -> Dict[str, Any]:
    """Validates configuration settings and returns any issues found."""
    issues = {}
    
    # Check directory existence
    if not os.path.exists(DAILY_MODELS_DIR):
        issues["DAILY_MODELS_DIR"] = f"Directory does not exist: {DAILY_MODELS_DIR}"
    if not os.path.exists(WEEKLY_MODELS_DIR):
        issues["WEEKLY_MODELS_DIR"] = f"Directory does not exist: {WEEKLY_MODELS_DIR}"
    
    # Validate threshold values
    if DEFAULT_DAILY_STRONG_MOVE_THRESHOLD <= 0:
        issues["DEFAULT_DAILY_STRONG_MOVE_THRESHOLD"] = "Must be greater than 0"
    if STRONG_MOVE_CONFIDENCE_THRESHOLD <= 0 or STRONG_MOVE_CONFIDENCE_THRESHOLD > 1.0:
        issues["STRONG_MOVE_CONFIDENCE_THRESHOLD"] = "Must be between 0 and 1"
    
    return issues

def get_daily_model_path(classifier_name: str) -> str:
    """Returns the model path for a given classifier name."""
    return os.path.join(DAILY_MODELS_DIR, f"{classifier_name}.pkl")