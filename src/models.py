"""
SQLAlchemy ORM models for the Odia Panchang database.
"""

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class PanchangDay(Base):
    __tablename__ = "panchang_days"

    date             = Column(String, primary_key=True)   # YYYY-MM-DD
    vara_en          = Column(String)
    vara_or          = Column(String)
    soura_masa_en    = Column(String)
    soura_masa_or    = Column(String)
    chandra_masa_en  = Column(String)
    chandra_masa_or  = Column(String)
    paksha_en        = Column(String)
    paksha_or        = Column(String)
    tithi_num        = Column(Integer)
    tithi_en         = Column(String)
    tithi_or         = Column(String)
    nakshatra_en     = Column(String)
    nakshatra_or     = Column(String)
    yoga_en          = Column(String)
    yoga_or          = Column(String)
    karana_en        = Column(String)
    karana_or        = Column(String)
    sunrise          = Column(String)
    sunset           = Column(String)

    festivals        = relationship("Festival", back_populates="day", cascade="all, delete-orphan")


class Festival(Base):
    __tablename__ = "festivals"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    date        = Column(String, ForeignKey("panchang_days.date"), nullable=False)
    name_en     = Column(String, nullable=False)
    name_or     = Column(String, nullable=False)
    tradition   = Column(String, nullable=False)   # common / jagannath / biraja
    description = Column(Text)

    day = relationship("PanchangDay", back_populates="festivals")


def get_engine(database_url: str):
    return create_engine(database_url, echo=False, future=True)


def get_session_factory(engine):
    return sessionmaker(bind=engine)


def init_db(engine):
    Base.metadata.create_all(bind=engine)
