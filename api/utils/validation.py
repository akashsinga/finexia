# api/utils/validation.py

from typing import List, Dict, Any
import re


def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format"""
    # Typically uppercase letters, sometimes with numbers
    pattern = r"^[A-Z0-9\.]{1,10}$"
    return bool(re.match(pattern, symbol))


def validate_model_parameters(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Validate model training parameters"""
    errors = []

    if "max_days" in params and (params["max_days"] < 1 or params["max_days"] > 30):
        errors.append({"field": "max_days", "message": "max_days must be between 1 and 30"})

    if "threshold" in params and (params["threshold"] < 0.5 or params["threshold"] > 20):
        errors.append({"field": "threshold", "message": "threshold must be between 0.5 and 20"})

    valid_classifiers = ["randomforest", "xgboost", "lightgbm"]

    if "move_classifier" in params and params["move_classifier"] not in valid_classifiers:
        errors.append({"field": "move_classifier", "message": f"move_classifier must be one of: {', '.join(valid_classifiers)}"})

    if "direction_classifier" in params and params["direction_classifier"] not in valid_classifiers:
        errors.append({"field": "direction_classifier", "message": f"direction_classifier must be one of: {', '.join(valid_classifiers)}"})

    return errors
