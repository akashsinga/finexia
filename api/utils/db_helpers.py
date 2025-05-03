# api/utils/db_helpers.py
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Type, TypeVar, Optional
from datetime import date

T = TypeVar("T")


def paginate_query(query, skip: int, limit: int):
    """Apply pagination to a query"""
    return query.offset(skip).limit(limit)


def filter_by_date_range(query, model_class, from_date: Optional[date], to_date: Optional[date]):
    """Filter query by date range"""
    if from_date:
        query = query.filter(model_class.date >= from_date)
    if to_date:
        query = query.filter(model_class.date <= to_date)
    return query


def get_latest_record(db: Session, model_class: Type[T], filter_dict: Dict[str, Any]) -> Optional[T]:
    """Get the latest record of a model based on date"""
    query = db.query(model_class)

    # Apply filters
    for key, value in filter_dict.items():
        if hasattr(model_class, key):
            query = query.filter(getattr(model_class, key) == value)

    # Order by date if model has date column
    if hasattr(model_class, "date"):
        query = query.order_by(model_class.date.desc())

    return query.first()


def bulk_insert(db: Session, model_class: Type[T], records: List[Dict[str, Any]]) -> bool:
    """Bulk insert records into a table"""
    try:
        db_objects = [model_class(**record) for record in records]
        db.bulk_save_objects(db_objects)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error during bulk insert: {str(e)}")
        return False
