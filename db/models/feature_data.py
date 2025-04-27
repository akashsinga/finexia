# db/models/feature_data.py

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, UniqueConstraint
from db.base_class import Base

class FeatureData(Base):
    __tablename__ = "features_data"
    __table_args__ = (
        UniqueConstraint('trading_symbol', 'exchange', 'date', name='unique_feature_per_day'),
    )

    id = Column(Integer, primary_key=True, index=True)
    trading_symbol = Column(String, nullable=False, index=True)
    exchange = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # Price Action Features
    gap_pct = Column(Float)
    hl_range = Column(Float)
    body_to_range_ratio = Column(Float)

    # Trend / Momentum Features
    distance_from_ema_5 = Column(Float)
    return_3d = Column(Float)
    atr_5 = Column(Float)

    # Volume / Volatility Features
    volume_spike_ratio = Column(Float)
    range_compression_ratio = Column(Float)
    volatility_squeeze = Column(Float)
    trend_zone_strength = Column(Float)

    # Contextual
    fo_eligible = Column(Boolean, default=False)
