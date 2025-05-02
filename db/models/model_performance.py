# db/models/model_performance.py (New File)

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Index
from sqlalchemy.sql import func
from db.base_class import Base

class ModelPerformance(Base):
    __tablename__ = "model_performance"
    __table_args__ = (
        Index('idx_performance_symbol', 'trading_symbol'),
        Index('idx_performance_date', 'evaluation_date'),
    )

    id = Column(Integer, primary_key=True, index=True)
    trading_symbol = Column(String, nullable=False, index=True)
    model_type = Column(String, nullable=False)  # "move" or "direction"
    training_date = Column(Date, nullable=False)
    evaluation_date = Column(Date, nullable=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    avg_days_to_fulfill = Column(Float, nullable=True)
    sensitivity_threshold = Column(Float, nullable=False)
    predictions_count = Column(Integer, nullable=False, default=0)
    successful_count = Column(Integer, nullable=False, default=0)
    effective_features = Column(String, nullable=True)  # Store as JSON string of array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ModelPerformance(symbol={self.trading_symbol}, model={self.model_type}, acc={self.accuracy:.2f}, f1={self.f1_score:.2f})>"
    