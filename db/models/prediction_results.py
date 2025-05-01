# db/models/prediction_result.py

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from db.base_class import Base

class PredictionResult(Base):
    __tablename__ = "prediction_results"
    __table_args__ = (
        UniqueConstraint('trading_symbol', 'date', name='unique_prediction_per_day'),
        Index('idx_prediction_symbol_date', 'trading_symbol', 'date'),  # Optimized index for common queries
        Index('idx_prediction_date', 'date'),  # For date-based queries
        Index('idx_prediction_confidence', 'strong_move_confidence'),  # For filtering high-confidence predictions
    )

    id = Column(Integer, primary_key=True, index=True)
    trading_symbol = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    strong_move_confidence = Column(Float, nullable=False)
    direction_prediction = Column(String, nullable=True)  # "UP" or "DOWN"
    direction_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    model_config_hash = Column(String, nullable=True)  # For traceability
    
    def __repr__(self):
        direction = self.direction_prediction if self.direction_prediction else "NONE"
        return f"<PredictionResult(symbol={self.trading_symbol}, date={self.date}, move_conf={self.strong_move_confidence:.2f}, dir={direction})>"

    @property
    def is_strong_move(self):
        """Whether prediction indicates a strong move is likely."""
        from core.config import STRONG_MOVE_CONFIDENCE_THRESHOLD
        return self.strong_move_confidence >= STRONG_MOVE_CONFIDENCE_THRESHOLD
    
    @property 
    def signal_type(self):
        """Get the signal type (UP, DOWN, NONE)."""
        if not self.is_strong_move:
            return "NONE"
        return self.direction_prediction if self.direction_prediction else "NONE"