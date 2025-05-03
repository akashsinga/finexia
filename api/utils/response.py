# api/utils/response.py
from typing import Any, Dict, List, Optional


def success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """Format successful response"""
    response = {"status": "success", "data": data}

    if message:
        response["message"] = message

    return response


def error_response(message: str, errors: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Format error response"""
    response = {"status": "error", "message": message}

    if errors:
        response["errors"] = errors

    return response
  