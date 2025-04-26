from sqlalchemy import create_engine, Column, DateTime, Numeric, Integer
from .database import Base


class Reading(Base):
    __tablename__ = 'readings'

    time = Column(DateTime, nullable=False, primary_key=True)
    device_id = Column(Integer, nullable=False, primary_key=True)
    A_plus = Column(Numeric(6, 3), nullable=True)
    A_minus = Column(Numeric(6, 3), nullable=True)
    R_plus = Column(Numeric(6, 3), nullable=True)
    R_minus = Column(Numeric(6, 3), nullable=True)