# db/models/symbol.py

from sqlalchemy import Column, String, Integer, Boolean, UniqueConstraint, DateTime, Index
from sqlalchemy.sql import func
from db.base_class import Base

class Symbol(Base):
    __tablename__ = "symbols"
    __table_args__ = (
        UniqueConstraint('trading_symbol', 'exchange', name='unique_trading_symbol_exchange'),
        Index('idx_symbol_active', 'active'),  # For filtering active symbols
        Index('idx_symbol_fo', 'fo_eligible'),  # For filtering F&O eligible symbols
    )

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    trading_symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    instrument_type = Column(String, nullable=False)
    segment = Column(String)
    lot_size = Column(Integer, nullable=True)
    active = Column(Boolean, default=True, index=True)
    fo_eligible = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Symbol(id={self.id}, symbol={self.trading_symbol}, exchange={self.exchange}, active={self.active})>"

    @property
    def is_equity(self):
        """Check if symbol is an equity."""
        return self.instrument_type == "EQUITY"
    
    @property
    def display_name(self):
        """Return a display-friendly name."""
        return f"{self.trading_symbol} ({self.exchange})"