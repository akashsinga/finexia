# db/models/feature_data.py

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, UniqueConstraint, DateTime
from sqlalchemy.sql import func
from db.base_class import Base

class FeatureData(Base):
    __tablename__ = "features_data"
    __table_args__ = (UniqueConstraint('trading_symbol', 'exchange', 'date', name='unique_feature_per_day'),)

    id = Column(Integer, primary_key=True, index=True)
    trading_symbol = Column(String, nullable=False, index=True)
    exchange = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    week_day = Column(Integer)

    gap_pct = Column(Float)
    hl_range = Column(Float)
    body_to_range_ratio = Column(Float)
    distance_from_ema_5 = Column(Float)
    return_3d = Column(Float)
    atr_5 = Column(Float)
    volume_spike_ratio = Column(Float)
    range_compression_ratio = Column(Float)
    volatility_squeeze = Column(Float)
    trend_zone_strength = Column(Float)
    fo_eligible = Column(Boolean, default=False)

    rsi_14 = Column(Float)
    close_ema50_gap_pct = Column(Float)
    open_gap_pct = Column(Float)
    macd_histogram = Column(Float)
    atr_14_normalized = Column(Float)
    percent_move = Column(Float)

    # New additions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    source_tag = Column(String, default="default")
