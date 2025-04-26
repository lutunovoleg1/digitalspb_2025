from sqlalchemy import create_engine, Column, DateTime, Numeric, Integer, Text
from .database import Base


class Reading(Base):
    __tablename__ = 'readings'

    time = Column(DateTime, nullable=False, primary_key=True)
    device_id = Column(Text, nullable=False, primary_key=True)
    a_plus = Column(Numeric(6, 3), nullable=True)
    a_minus = Column(Numeric(6, 3), nullable=True)
    r_plus = Column(Numeric(6, 3), nullable=True)
    r_minus = Column(Numeric(6, 3), nullable=True)