# db/models/symbol.py

from sqlalchemy import Column, String, Integer, Boolean
from db.base_class import Base

class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, nullable=False)
    trading_symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    instrument_type = Column(String, nullable=False)
    segment = Column(String)
    lot_size = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)
    fo_eligible = Column(Boolean, default=False)
