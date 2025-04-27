# db/models/eod_data.py

from sqlalchemy import Column, String, Integer, Float, Date, Boolean, BigInteger, UniqueConstraint
from db.base_class import Base

class EODData(Base):
    __tablename__ = "eod_data"
    __table_args__ = (
        UniqueConstraint('trading_symbol', 'exchange', 'date', name='unique_eod_per_day'),
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
