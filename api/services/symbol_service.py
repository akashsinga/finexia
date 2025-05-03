# api/services/symbol_service.py - Updated version

from sqlalchemy.orm import Session
from typing import List, Optional
from db.models.symbol import Symbol as SymbolModel
from api.models.symbol import SymbolCreate, SymbolUpdate


def get_symbol(db: Session, symbol_id: int) -> Optional[SymbolModel]:
    """Get a symbol by ID"""
    
    return db.query(SymbolModel).filter(SymbolModel.id == symbol_id).first()


def get_symbol_by_trading_symbol(db: Session, trading_symbol: str, exchange: str) -> Optional[SymbolModel]:
    """Get a symbol by trading symbol and exchange"""

    return db.query(SymbolModel).filter(SymbolModel.trading_symbol == trading_symbol, SymbolModel.exchange == exchange).first()


def get_symbols(db: Session, active_only: bool = True, fo_eligible: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[SymbolModel]:
    """Get list of symbols with filtering"""

    query = db.query(SymbolModel)

    if active_only:
        query = query.filter(SymbolModel.active)

    if fo_eligible is not None:
        query = query.filter(SymbolModel.fo_eligible == fo_eligible)

    return query.order_by(SymbolModel.trading_symbol).offset(skip).limit(limit).all()


def create_symbol(db: Session, symbol: SymbolCreate) -> SymbolModel:
    """Create a new symbol"""

    db_symbol = SymbolModel(security_id=symbol.security_id, trading_symbol=symbol.trading_symbol, exchange=symbol.exchange, name=symbol.name, instrument_type=symbol.instrument_type, segment=symbol.segment, lot_size=symbol.lot_size, active=True, fo_eligible=symbol.fo_eligible)

    db.add(db_symbol)
    db.commit()
    db.refresh(db_symbol)

    return db_symbol


def update_symbol(db: Session, symbol_id: int, symbol: SymbolUpdate) -> Optional[SymbolModel]:
    """Update a symbol"""
    
    db_symbol = get_symbol(db, symbol_id)
    if not db_symbol:
        return None

    # Update fields if provided
    if symbol.name is not None:
        db_symbol.name = symbol.name
    if symbol.active is not None:
        db_symbol.active = symbol.active
    if symbol.fo_eligible is not None:
        db_symbol.fo_eligible = symbol.fo_eligible
    if symbol.lot_size is not None:
        db_symbol.lot_size = symbol.lot_size

    db.commit()
    db.refresh(db_symbol)

    return db_symbol


def delete_symbol(db: Session, symbol_id: int) -> bool:
    """Delete a symbol (mark as inactive)"""
    
    db_symbol = get_symbol(db, symbol_id)
    if not db_symbol:
        return False

    db_symbol.active = False
    db.commit()

    return True
