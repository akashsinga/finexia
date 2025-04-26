# db/models/symbol.py

from sqlalchemy import Column, String, Integer, Boolean, UniqueConstraint
from db.base_class import Base

class Symbol(Base):
    __tablename__ = "symbols"
    __table_args__ = (
        UniqueConstraint('trading_symbol', 'exchange', name='unique_trading_symbol_exchange'),
    )

    id = Column(Integer, primary_key=True, index=True)
    security_id = Column(String, nullable=False)  # <-- NEW FIELD
    exchange = Column(String, nullable=False)
    trading_symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    instrument_type = Column(String, nullable=False)
    segment = Column(String)
    lot_size = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)
    fo_eligible = Column(Boolean, default=False)
