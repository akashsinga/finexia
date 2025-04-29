# db/models/prediction_result.py

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, UniqueConstraint
from db.base_class import Base
from datetime import datetime

class PredictionResult(Base):
    __tablename__ = "prediction_results"
    __table_args__ = (
        UniqueConstraint('trading_symbol', 'date', name='unique_prediction_per_day'),
    )

    id = Column(Integer, primary_key=True, index=True)
    trading_symbol = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    strong_move_confidence = Column(Float, nullable=False)
    direction_prediction = Column(String, nullable=True)  # "UP" or "DOWN"
    direction_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
