# app\schemas.py
from pydantic import BaseModel
'''
BaseModel → Pydantic’in temel sınıfı.

Tüm veri modelleri bundan türetilir.

Sağladığı özellikler: veri doğrulama, tip kontrolü, otomatik JSON dönüşümü.
'''
from datetime import datetime
'''
datetime → tarih ve saat objesi.

Hava kalitesi ve hava durumu kayıtlarının zamanını tutmak için kullanılır.
'''
from typing import Optional
'''
Optional → bir alanın opsiyonel olabileceğini belirtir (None olabilir).
'''

# ----------------------------
# Hava Kalitesi
# ----------------------------
class AirQualityBase(BaseModel):
    city_id: int
    aqi: float
    source: str
'''
AirQualityBase → temel hava kalitesi modeli.

city_id → şehir ID’si

aqi → Hava Kalitesi İndeksi (Air Quality Index)

source → veriyi sağlayan kaynak (örn. AirNow, TEMPO)

Bu sınıf request payload (POST edilen veri) için kullanılır.
'''
class AirQualityResponse(AirQualityBase):
    id: int
    timestamp: datetime
    '''
    AirQualityResponse → DB’den döndürülecek response modeli.

Base sınıftan (AirQualityBase) türetilmiş, ek olarak:

id → veritabanındaki birincil anahtar

timestamp → kayıt zamanı
    '''

    class Config:
        orm_mode = True  # SQLAlchemy → Pydantic dönüşümü
        '''
        orm_mode = True → SQLAlchemy modellerini Pydantic objesine otomatik çevirir.

Yani endpoint’te DB objesi (models.AirQualityData) döndürülürse, FastAPI bunu JSON’a çevirir.
        '''

# ----------------------------
# Hava Durumu
# ----------------------------
class WeatherBase(BaseModel):
    city_id: int
    temperature: float
    humidity: float
    source: str
    '''
    Temel hava durumu modeli:

city_id → şehir ID’si

temperature → sıcaklık

humidity → nem

source → veri kaynağı
    '''

class WeatherResponse(WeatherBase):
    id: int
    timestamp: datetime
    '''
    Hava durumu response modeli.

Ek alanlar: id ve timestamp
    '''

    class Config:
        orm_mode = True
        '''
        DB objelerini JSON’a çevirmek için orm_mode = True kullanılır.

Artık endpoint’te direkt db_obj döndürürsen FastAPI otomatik JSON’a çevirir.
✅ Özet:

Base modeller → POST/PUT istekleri için kullanılır.

Response modeller → GET istekleri için DB’den dönecek verileri tipli JSON olarak döndürür.

orm_mode = True → SQLAlchemy objelerini Pydantic JSON’ına çevirir.
        '''

# Artık endpointlerde return db_obj yaptığında FastAPI otomatik JSON’a çevirir.