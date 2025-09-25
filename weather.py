# app/api/v1/routers/weather.py
from fastapi import APIRouter, Depends, HTTPException
'''
FastAPI’den üç şeyi içe aktarıyoruz:
APIRouter → Endpoint’leri organize etmek ve modüler bir router oluşturmak için.
Depends → Dependency Injection (bağımlılık yönetimi) için, örneğin DB oturumu almak.
HTTPException → Hata durumlarını HTTP kodu ile döndürmek için.
'''
from sqlalchemy.orm import Session
'''
SQLAlchemy’nin Session sınıfı.
Veritabanı ile iletişim kurmak, sorgu yapmak, veri eklemek veya güncellemek için kullanılır.
'''
from datetime import datetime
'''
Python’un tarih ve saat yönetim kütüphanesi.
Örneğin, hava durumu ölçümünün zamanını kaydetmek için.
'''
from app.db.session import get_db
'''
get_db → DB oturumu sağlayan fonksiyon.
Depends(get_db) ile endpoint’e aktarılır, böylece her çağrıda DB oturumu açılır ve kapanır.
'''
from app import crud
'''
CRUD modülü: DB işlemleri için kullanılan fonksiyonlar.
upsert_weather veya get_last_24h_weather gibi fonksiyonlar burada tanımlanmıştır.
'''
from pydantic import BaseModel
'''
BaseModel → API’ye gelen JSON verisini doğrulamak ve tip güvenliği sağlamak için.
Pydantic modeli, FastAPI ile otomatik veri doğrulama sağlar.
'''

router = APIRouter()
'''
Yeni bir FastAPI router oluşturuyoruz.
Bu router’a endpoint ekleyip daha sonra ana FastAPI uygulamasına bağlayabiliriz.
'''

class WeatherCreate(BaseModel):
    location_id: int
    timestamp: datetime
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    pressure: float | None = None
'''
WeatherCreate → API’ye gönderilecek hava durumu verisi için Pydantic modeli.
Alanlar:
location_id: int → Hangi konum için veri geldiğini belirler (zorunlu).
timestamp: datetime → Ölçüm zamanı (zorunlu).
temperature, humidity, wind_speed, pressure → Hava durumu verileri, opsiyonel (None default değeri).
'''

@router.get("/latest")
# Bu endpoint /latest yoluna gelen GET isteğini yakalar.
# Amaç: Belirtilen konum için son 24 saatin hava durumu verilerini almak.

def get_latest_weather(location_id: int, db: Session = Depends(get_db)):
    '''
    Endpoint fonksiyonu:
    location_id: int → URL parametresi olarak konum ID’si.
    db: Session = Depends(get_db) → DB oturumu, FastAPI otomatik olarak sağlar.
    '''
    recs = crud.get_last_24h_weather(db, location_id)
    '''
    get_last_24h_weather → DB’den son 24 saatin hava durumu kayıtlarını çekiyor.
    recs → bir liste döner, her eleman bir dict veya model nesnesi olabilir.
    '''
    if not recs:
        raise HTTPException(status_code=404, detail="No weather data found")
    '''
        Eğer veri yoksa:
        HTTP 404 Not Found hatası döndürülür.
        detail → kullanıcıya gösterilecek açıklama mesajı.
    '''
    # return latest entry
    return recs[-1]
'''
Liste içindeki son kayıt (recs[-1]) alınır ve JSON olarak döndürülür.
Bu, son ölçümün en güncel veri olduğunu garanti eder.
'''


@router.post("/", status_code=201)
# Bu endpoint / yoluna POST isteği geldiğinde çalışır.
# status_code=201 → Yeni veri oluşturulduğunda HTTP 201 Created döndürür.

def create_or_update_weather(payload: WeatherCreate, db: Session = Depends(get_db)):
    '''
    POST endpoint fonksiyonu:
    payload: WeatherCreate → İstek gövdesinde JSON olarak gelen veri, Pydantic ile doğrulanır.
    db: Session = Depends(get_db) → DB oturumu.
    '''
    obj = crud.upsert_weather(
        db,
        location_id=payload.location_id,
        timestamp=payload.timestamp,
        temperature=payload.temperature,
        humidity=payload.humidity,
        wind_speed=payload.wind_speed,
        pressure=payload.pressure,
    )
    '''
    upsert_weather → Eğer kayıt varsa günceller, yoksa yeni kayıt ekler (UPSERT).
    payload’daki tüm alanlar parametre olarak geçiliyor.
    '''
    return obj
'''
Oluşturulan veya güncellenen kayıt JSON olarak döndürülür.
FastAPI dict veya Pydantic modelini otomatik JSON’a çevirir.

💡 Özet Akış:

GET /latest → son 24 saatin hava durumu verilerini DB’den alır, son kaydı döndürür.
POST / → Gelen hava durumu verisini DB’ye ekler veya günceller.
crud modülü DB ile tüm CRUD işlemlerini yönetir.
Depends(get_db) ile her çağrıda DB oturumu sağlanır.
Pydantic odeli (WeatherCreate) veri doğrulama sağlar.
'''