from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    device_key = Column(String(length=40), ForeignKey("devices.device_key"))
    inside_temp = Column(Float)
    outside_temp = Column(Float)
    inside_humidity = Column(Float)
    outside_humidity = Column(Float)
    current_capacity = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.now(tz=timezone('America/Los_Angeles')))

    device = relationship("Device", back_populates="measurements")


class Device(Base):
    __tablename__ = "devices"
    device_key = Column(String(length=40), unique=True, primary_key=True)
    name = Column(String)
    hardware = Column(String)
    firmware = Column(String)
    software = Column(String)

    measurements = relationship("Measurement", back_populates="device")