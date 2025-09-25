# app\crud.py
from sqlalchemy.orm import Session
'''
SQLAlchemy’nin Session sınıfını import ediyoruz.

db: Session parametresi ile DB üzerinde sorgu ve commit işlemleri yapabiliyoruz.
'''
from datetime import datetime, timedelta
'''
datetime → tarih/saat objesi oluşturmak için.

timedelta → belli bir süreyi ifade eder (örn. son 24 saat).
'''
from app import models
'''
ORM modellerini import ediyoruz (AirQualityData, WeatherData).

Bu modeller veritabanındaki tablolara karşılık geliyor.
'''

# ----------------------------
# Air Quality CRUD (AirQualityData)
# ----------------------------
def upsert_air_quality(db: Session, location_id: int, timestamp: datetime, aqi: float = None, pm25: float = None, pm10: float = None, o3: float = None, co: float = None, so2: float = None, source: str | None = None):
    '''
    upsert_air_quality → DB’de varsa güncelle, yoksa ekle fonksiyonu.

Parametreler: location_id, timestamp, AQI ve diğer gaz değerleri, opsiyonel source.
    '''
    # unique constraint on (location_id, timestamp)
    existing = (
        db.query(models.AirQualityData)
        .filter(models.AirQualityData.location_id == location_id, models.AirQualityData.timestamp == timestamp)
        .first()
    )
    '''
    DB’de bu lokasyon ve zaman için kayıt var mı kontrol ediliyor.

Eğer varsa → existing değişkeni dolacak.
    '''
    if existing:
        # update fields if provided
        if aqi is not None:
            existing.aqi = aqi
        if pm25 is not None:
            existing.pm25 = pm25
        if pm10 is not None:
            existing.pm10 = pm10
        if o3 is not None:
            existing.o3 = o3
        if co is not None:
            existing.co = co
        if so2 is not None:
            existing.so2 = so2
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
# Eğer kayıt varsa:

# Verilen değerler None değilse güncellenir.

# db.add(existing) → session’a ekle (update için de çalışır).

# db.commit() → değişiklikleri DB’ye yaz.

# db.refresh(existing) → DB’den en güncel objeyi al.

# return existing → güncellenmiş kaydı döndür.


    else:
        new = models.AirQualityData(
            location_id=location_id,
            timestamp=timestamp,
            aqi=aqi,
            pm25=pm25,
            pm10=pm10,
            o3=o3,
            co=co,
            so2=so2,
        )
        db.add(new)
        db.commit()
        db.refresh(new)
        return new
'''
Eğer kayıt yoksa → yeni bir AirQualityData objesi oluşturulur, DB’ye eklenir ve döndürülür.
'''

def get_latest_air_quality(db: Session, location_id: int):
    return (
        db.query(models.AirQualityData)
        .filter(models.AirQualityData.location_id == location_id)
        .order_by(models.AirQualityData.timestamp.desc())
        .first()
    )
'''
Belirli bir lokasyon için en son ölçümü getirir.

order_by(...desc()) → en güncel kayıt en üstte olur.

first() → sadece bir kayıt döner.
'''


def get_last_24h_air_quality(db: Session, location_id: int):
    since = datetime.utcnow() - timedelta(hours=24)
    return (
        db.query(models.AirQualityData)
        .filter(models.AirQualityData.location_id == location_id, models.AirQualityData.timestamp >= since)
        .order_by(models.AirQualityData.timestamp.asc())
        .all()
    )
'''
Son 24 saatteki AQI verilerini getirir.

timestamp >= since → sadece son 24 saat.

order_by(...asc()) → eski veriden yeni veriye sıralar.

all() → tüm kayıtları liste olarak döndürür.
'''

# ----------------------------
# Weather CRUD (WeatherData)
# ----------------------------
def upsert_weather(db: Session, location_id: int, timestamp: datetime, temperature: float = None, humidity: float = None, wind_speed: float = None, pressure: float = None, source: str | None = None):
    '''
    Hava durumu için upsert fonksiyonu.

Parametreler: temperature, humidity, wind_speed, pressure vb.
    '''
    existing = (
        db.query(models.WeatherData)
        .filter(models.WeatherData.location_id == location_id, models.WeatherData.timestamp == timestamp)
        .first()
    )
    '''
    DB’de bu lokasyon ve timestamp için kayıt var mı kontrol edilir.
    '''
    if existing:
        if temperature is not None:
            existing.temperature = temperature
        if humidity is not None:
            existing.humidity = humidity
        if wind_speed is not None:
            existing.wind_speed = wind_speed
        if pressure is not None:
            existing.pressure = pressure
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

     # Eğer kayıt varsa, verilen değerler güncellenir ve DB’ye commit edilir.
    else:
        new = models.WeatherData(
            location_id=location_id,
            timestamp=timestamp,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            pressure=pressure,
        )
        db.add(new)
        db.commit()
        db.refresh(new)
        return new
'''
Kayıt yoksa yeni bir obje oluşturulur, eklenir ve döndürülür.
'''


def get_last_24h_weather(db: Session, location_id: int):
    since = datetime.utcnow() - timedelta(hours=24)
    return (
        db.query(models.WeatherData)
        .filter(models.WeatherData.location_id == location_id, models.WeatherData.timestamp >= since)
        .order_by(models.WeatherData.timestamp.asc())
        .all()
    
    )
'''
Son 24 saatteki hava durumu verilerini getirir.

Eski veriden yeni veriye sıralar.

Tüm kayıtları liste olarak döndürür.

✅ Özet:

upsert_air_quality / upsert_weather → var olan kaydı günceller, yoksa ekler.

get_latest_air_quality → en güncel AQI kaydını döndürür.

get_last_24h_air_quality / get_last_24h_weather → son 24 saatlik verileri listeler.
'''