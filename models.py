# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from app.db.session import Base

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)

class Locations(Base):
    __tablename__ = "locations"
    location_id = Column(Integer, primary_key=True, autoincrement=True)
    city_name = Column(String(100), nullable=False)
    latitude = Column(Numeric(9,6), nullable=False)
    longitude = Column(Numeric(9,6), nullable=False)
    __table_args__ = (UniqueConstraint("city_name", "latitude", "longitude", name="uniq_locations"),)

class TempoData(Base):
    __tablename__ = "tempodata"
    tempo_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    o3 = Column(Float)
    no2 = Column(Float)
    so2 = Column(Float)
    co = Column(Float)
    aerosol_index = Column(Float)
    location = relationship("Locations")
    __table_args__ = (UniqueConstraint("location_id", "timestamp", name="uniq_tempodata"),)

class AirQualityData(Base):
    __tablename__ = "airqualitydata"
    aq_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    aqi = Column(Integer)
    pm25 = Column(Float)
    pm10 = Column(Float)
    o3 = Column(Float)
    co = Column(Float)
    so2 = Column(Float)
    location = relationship("Locations")
    __table_args__ = (UniqueConstraint("location_id", "timestamp", name="uniq_airqualitydata"),)

class WeatherData(Base):
    __tablename__ = "weatherdata"
    weather_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    pressure = Column(Float)
    location = relationship("Locations")
    __table_args__ = (UniqueConstraint("location_id", "timestamp", name="uniq_weatherdata"),)

class Predictions(Base):
    __tablename__ = "predictions"
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    predicted_aqi = Column(Integer)
    model_version = Column(String(50))
    location = relationship("Locations")
    __table_args__ = (UniqueConstraint("location_id", "timestamp", "model_version", name="uniq_predictions"),)
