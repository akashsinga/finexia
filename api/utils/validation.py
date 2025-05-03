# api/utils/validation.py - Expanded validation utilities
from typing import List, Dict, Any, Optional
import re
from datetime import date

def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format"""
    # Typically uppercase letters, sometimes with numbers
    pattern = r"^[A-Z0-9\.]{1,10}$"
    return bool(re.match(pattern, symbol))

def validate_date_range(from_date: Optional[date], to_date: Optional[date], max_days: int = 365) -> List[Dict[str, str]]:
    """Validate date range parameters"""
    errors = []
    
    if from_date and to_date and from_date > to_date:
        errors.append({"field": "from_date", "message": "from_date must be before to_date"})
    
    if from_date and to_date and (to_date - from_date).days > max_days:
        errors.append({"field": "date_range", "message": f"Date range cannot exceed {max_days} days"})
        
    return errors

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

def validate_pagination(skip: int, limit: int, max_limit: int = 1000) -> List[Dict[str, str]]:
    """Validate pagination parameters"""
    errors = []
    
    if skip < 0:
        errors.append({"field": "skip", "message": "skip must be a non-negative integer"})
        
    if limit < 1:
        errors.append({"field": "limit", "message": "limit must be a positive integer"})
        
    if limit > max_limit:
        errors.append({"field": "limit", "message": f"limit cannot exceed {max_limit}"})
        
    return errors

def validate_user_input(username: str, email: str, password: Optional[str] = None) -> List[Dict[str, str]]:
    """Validate user input fields"""
    errors = []
    
    # Username validation
    if not re.match(r"^[a-zA-Z0-9_-]{3,20}$", username):
        errors.append({"field": "username", "message": "Username must be 3-20 characters and contain only letters, numbers, underscore, or hyphen"})
    
    # Email validation (basic pattern)
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        errors.append({"field": "email", "message": "Invalid email format"})
    
    # Password validation if provided
    if password:
        if len(password) < 8:
            errors.append({"field": "password", "message": "Password must be at least 8 characters long"})
            
        if not re.search(r"[A-Z]", password):
            errors.append({"field": "password", "message": "Password must contain at least one uppercase letter"})
            
        if not re.search(r"[a-z]", password):
            errors.append({"field": "password", "message": "Password must contain at least one lowercase letter"})
            
        if not re.search(r"[0-9]", password):
            errors.append({"field": "password", "message": "Password must contain at least one digit"})
    
    return errors