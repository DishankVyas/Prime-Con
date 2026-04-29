import contextlib
from datetime import date, time
from typing import Generator
from sqlalchemy import create_engine, String, Date, Float, Integer, ForeignKey, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

class VBAK(Base):
    __tablename__ = "vbak"
    vbeln: Mapped[str] = mapped_column(String, primary_key=True)
    erdat: Mapped[date] = mapped_column(Date)
    kunnr: Mapped[str] = mapped_column(String)
    netwr: Mapped[float] = mapped_column(Float)
    waerk: Mapped[str] = mapped_column(String(3))
    vkorg: Mapped[str] = mapped_column(String(4))
    vtweg: Mapped[str] = mapped_column(String(2))
    spart: Mapped[str] = mapped_column(String(2))
    auart: Mapped[str] = mapped_column(String(4))
    vbtyp: Mapped[str] = mapped_column(String(1))

class VBAP(Base):
    __tablename__ = "vbap"
    vbeln: Mapped[str] = mapped_column(String, ForeignKey("vbak.vbeln"), primary_key=True)
    posnr: Mapped[str] = mapped_column(String(6), primary_key=True)
    matnr: Mapped[str] = mapped_column(String)
    arktx: Mapped[str] = mapped_column(String(40))
    kwmeng: Mapped[float] = mapped_column(Float)
    meins: Mapped[str] = mapped_column(String(3))
    netpr: Mapped[float] = mapped_column(Float)
    werks: Mapped[str] = mapped_column(String(4))
    lgort: Mapped[str] = mapped_column(String(4))

class BKPF(Base):
    __tablename__ = "bkpf"
    bukrs: Mapped[str] = mapped_column(String(4), primary_key=True)
    belnr: Mapped[str] = mapped_column(String(10), primary_key=True)
    gjahr: Mapped[int] = mapped_column(Integer, primary_key=True)
    blart: Mapped[str] = mapped_column(String(2))
    bldat: Mapped[date] = mapped_column(Date)
    budat: Mapped[date] = mapped_column(Date)
    xblnr: Mapped[str] = mapped_column(String(16))
    bktxt: Mapped[str] = mapped_column(String(25))
    waers: Mapped[str] = mapped_column(String(3))
    usnam: Mapped[str] = mapped_column(String(12))

class BSEG(Base):
    __tablename__ = "bseg"
    bukrs: Mapped[str] = mapped_column(String(4), primary_key=True)
    belnr: Mapped[str] = mapped_column(String(10), primary_key=True)
    gjahr: Mapped[int] = mapped_column(Integer, primary_key=True)
    buzei: Mapped[str] = mapped_column(String(3), primary_key=True)
    hkont: Mapped[str] = mapped_column(String(10))
    shkzg: Mapped[str] = mapped_column(String(1))
    dmbtr: Mapped[float] = mapped_column(Float)
    wrbtr: Mapped[float] = mapped_column(Float)
    kostl: Mapped[str] = mapped_column(String(10))
    prctr: Mapped[str] = mapped_column(String(10))
    mwskz: Mapped[str] = mapped_column(String(2))
    zterm: Mapped[str] = mapped_column(String(4))

class EKKO(Base):
    __tablename__ = "ekko"
    ebeln: Mapped[str] = mapped_column(String(10), primary_key=True)
    bukrs: Mapped[str] = mapped_column(String(4))
    bsart: Mapped[str] = mapped_column(String(4))
    lifnr: Mapped[str] = mapped_column(String(10))
    ekgrp: Mapped[str] = mapped_column(String(3))
    bedat: Mapped[date] = mapped_column(Date)
    waers: Mapped[str] = mapped_column(String(3))
    zterm: Mapped[str] = mapped_column(String(4))
    inco1: Mapped[str] = mapped_column(String(3))

class EKPO(Base):
    __tablename__ = "ekpo"
    ebeln: Mapped[str] = mapped_column(String, ForeignKey("ekko.ebeln"), primary_key=True)
    ebelp: Mapped[str] = mapped_column(String(5), primary_key=True)
    matnr: Mapped[str] = mapped_column(String)
    txz01: Mapped[str] = mapped_column(String(40))
    menge: Mapped[float] = mapped_column(Float)
    meins: Mapped[str] = mapped_column(String(3))
    netpr: Mapped[float] = mapped_column(Float)
    peinh: Mapped[float] = mapped_column(Float)
    werks: Mapped[str] = mapped_column(String(4))
    eindt: Mapped[date] = mapped_column(Date)
    knttp: Mapped[str] = mapped_column(String(1))

class MSEG(Base):
    __tablename__ = "mseg"
    mblnr: Mapped[str] = mapped_column(String(10), primary_key=True)
    mjahr: Mapped[int] = mapped_column(Integer, primary_key=True)
    zeile: Mapped[str] = mapped_column(String(4), primary_key=True)
    bwart: Mapped[str] = mapped_column(String(3))
    matnr: Mapped[str] = mapped_column(String)
    werks: Mapped[str] = mapped_column(String(4))
    lgort: Mapped[str] = mapped_column(String(4))
    menge: Mapped[float] = mapped_column(Float)
    meins: Mapped[str] = mapped_column(String(3))
    dmbtr: Mapped[float] = mapped_column(Float)
    kostl: Mapped[str] = mapped_column(String(10))
    aufnr: Mapped[str] = mapped_column(String(12))
    ebeln: Mapped[str] = mapped_column(String(10))
    ebelp: Mapped[str] = mapped_column(String(5))

class AUFK(Base):
    __tablename__ = "aufk"
    aufnr: Mapped[str] = mapped_column(String(12), primary_key=True)
    auart: Mapped[str] = mapped_column(String(4))
    erdat: Mapped[date] = mapped_column(Date)
    matnr: Mapped[str] = mapped_column(String)
    werks: Mapped[str] = mapped_column(String(4))
    gamng: Mapped[float] = mapped_column(Float)
    gmein: Mapped[str] = mapped_column(String(3))
    gstrs: Mapped[date] = mapped_column(Date)
    gltrs: Mapped[date] = mapped_column(Date)
    gstri: Mapped[date] = mapped_column(Date)
    getri: Mapped[date] = mapped_column(Date)
    igmng: Mapped[float] = mapped_column(Float)
    aueru: Mapped[str] = mapped_column(String(2))

class CDHDR(Base):
    __tablename__ = "cdhdr"
    changenr: Mapped[str] = mapped_column(String(10), primary_key=True)
    objectclas: Mapped[str] = mapped_column(String(10))
    objectid: Mapped[str] = mapped_column(String(90))
    udate: Mapped[date] = mapped_column(Date)
    utime: Mapped[time] = mapped_column(Time)
    username: Mapped[str] = mapped_column(String(12))
    tcode: Mapped[str] = mapped_column(String(20))

class CDPOS(Base):
    __tablename__ = "cdpos"
    changenr: Mapped[str] = mapped_column(String, ForeignKey("cdhdr.changenr"), primary_key=True)
    tabname: Mapped[str] = mapped_column(String(10), primary_key=True)
    fname: Mapped[str] = mapped_column(String(30), primary_key=True)
    chngind: Mapped[str] = mapped_column(String(1))
    value_new: Mapped[str] = mapped_column(String(255))
    value_old: Mapped[str] = mapped_column(String(255))

Base.metadata.create_all(engine)

@contextlib.contextmanager
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
