# db/models/eod_data.py

from sqlalchemy import Column, String, Integer, Float, Date, Boolean, BigInteger, UniqueConstraint, DateTime, Index
from sqlalchemy.sql import func
from db.base_class import Base

class EODData(Base):
    __tablename__ = "eod_data"
    __table_args__ = (
        UniqueConstraint('trading_symbol', 'exchange', 'date', name='unique_eod_per_day'),
        Index('idx_eod_data_symbol_date', 'trading_symbol', 'date'),  # Optimized index for common queries
        Index('idx_eod_data_date', 'date'),  # For date range queries
    )

    id = Column(Integer, primary_key=True, index=True)
    trading_symbol = Column(String, nullable=False, index=True)
    exchange = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    fo_eligible = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def hl_range(self):
        """Calculate high-low range."""
        return self.high - self.low
    
    @property
    def body_range(self):
        """Calculate body range (close-open)."""
        return abs(self.close - self.open)
    
    def __repr__(self):
        return f"<EODData(symbol={self.trading_symbol}, date={self.date}, close={self.close})>"