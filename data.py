# app/api/v1/routers/data.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.data_fetcher import fetch_weather_data, fetch_air_quality_data
from app.services import tempo_service
from app import crud

router = APIRouter()

# ----------------------------
# Weather + AQI veri çekme endpoint
# ----------------------------
@router.post("/fetch-and-save/{location_id}")
def fetch_and_save(
    location_id: int,
    city: str,
    lat: float,
    lon: float,
    db: Session = Depends(get_db)
):
    """
    Belirtilen konum için hava durumu ve AQI verilerini çekip DB'ye kaydeder
    """
    # Weather verisi
    weather = fetch_weather_data(lat, lon)
    crud.upsert_weather(db, location_id=location_id, **weather)

    # AirQuality verisi
    aqi = fetch_air_quality_data(city)
    if aqi:
        crud.upsert_air_quality(db, location_id=location_id, **aqi)

    return {
        "status": "success",
        "weather_timestamp": weather["timestamp"],
        "aqi_timestamp": aqi["timestamp"] if aqi else None
    }

# ----------------------------
# TEMPO veri çekme endpoint
# ----------------------------
@router.post("/fetch-tempo/{location_id}")
def fetch_tempo(location_id: int, db: Session = Depends(get_db)):
    """
    TEMPO L2 verilerini Harmony'den çekip DB'ye kaydeder
    """
    tempo_service.fetch_and_save_all(
        db=db,
        start_date="2025-09-01",
        end_date="2025-09-02",
        location_id=location_id
    )
    return {"status": "success"}
