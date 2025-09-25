# app/api/v1/routers/aqi.py
from fastapi import APIRouter, Depends, HTTPException
'''
from fastapi import ... → FastAPI kütüphanesinden belirli sınıf ve fonksiyonları içe aktarırız.
APIRouter → API endpoint’lerini (yani /latest veya / gibi URL yollarını) organize etmek için kullanılır. Bir nevi “mini FastAPI uygulaması” gibi düşünebilirsin. Kodun daha modüler ve yönetilebilir olmasını sağlar.
Depends → Dependency Injection (bağımlılık yönetimi) için kullanılır. Örneğin, her endpoint’in bir DB bağlantısına ihtiyacı varsa, bunu Depends(get_db) ile sağlayabiliriz. Yani FastAPI otomatik olarak get_db fonksiyonunu çağırır ve sonucu endpoint’e verir.
HTTPException → API’de hata durumlarını HTTP kodlarıyla birlikte göndermek için kullanılır. Örneğin, veri bulunamazsa 404 Not Found döndürmek için.
'''
from sqlalchemy.orm import Session
'''
Session → SQLAlchemy’nin veritabanı oturum sınıfı. Veritabanı ile iletişimi sağlar.
Her endpoint’te db: Session kullanarak veritabanına sorgu gönderebiliriz.
'''
from datetime import datetime
'''
Python’un standart kütüphanesinden zaman ve tarih yönetimi için kullanılır.
Örneğin, bir ölçümün hangi tarihte alındığını kaydetmek için datetime kullanıyoruz.
'''
from app.db.session import get_db
'''
get_db → Veritabanı oturumu sağlayan fonksiyon.
Depends(get_db) ile endpoint’lerde kullanılır, böylece her çağrıda yeni bir DB oturumu açılır ve iş bittiğinde kapatılır.
'''
from app import crud, models
'''
crud → Veritabanı işlemlerini yapan modül. Create, Read, Update, Delete fonksiyonları burada tanımlanır.
models → SQLAlchemy veri modellerini içerir. Örneğin AirQuality tablosu burada tanımlanır.
'''
from pydantic import BaseModel
'''
BaseModel → FastAPI’de veri doğrulama ve şema tanımlamak için kullanılır.
API’ye gelen JSON verilerini doğrulamak ve tip güvenliği sağlamak için kullanıyoruz.
'''
router = APIRouter()
'''
Yeni bir API router oluşturuyoruz.
Artık bu router’a endpoint’ler (@router.get, @router.post) ekleyebiliriz.
Daha sonra bu router’ı ana uygulamaya (app.include_router(router)) ekleyeceğiz.
'''

class AQICreate(BaseModel):
    location_id: int
    timestamp: datetime
    aqi: float | None = None
    pm25: float | None = None
    pm10: float | None = None
    o3: float | None = None
    co: float | None = None
    so2: float | None = None
'''
AQICreate → API’ye gönderilecek veri için bir Pydantic modeli.
location_id: int → Ölçüm yapılan konumun ID’si. Zorunlu.
timestamp: datetime → Ölçüm zamanı. Zorunlu.
aqi, pm25, pm10, o3, co, so2 → Hava kalitesi değerleri. None ile varsayılan değer verildiği için opsiyonel.
Bu model, FastAPI’ye gelen JSON verisini otomatik doğrulama ve tip kontrolü yapmayı sağlar.
'''

@router.get("/latest")
def get_latest_aqi(location_id: int, db: Session = Depends(get_db)):
    record = crud.get_latest_air_quality(db, location_id)
    if record:
        return record
    raise HTTPException(status_code=404, detail="No data found")
'''
@router.get("/latest") → Bu fonksiyon /latest yoluna gelen GET isteğini yakalar.
location_id: int → URL parametresi olarak gelen konum ID’si.
db: Session = Depends(get_db) → FastAPI otomatik olarak get_db’yi çağırır ve DB oturumunu verir.
crud.get_latest_air_quality(db, location_id) → Veritabanından en son hava kalitesi kaydını çeker.
Eğer veri varsa, record döndürülür.
Veri yoksa, HTTP 404 Not Found hatası döndürülür.
'''

@router.post("/", status_code=201)
def create_or_update_aqi(payload: AQICreate, db: Session = Depends(get_db)):
    obj = crud.upsert_air_quality(
        db,
        location_id=payload.location_id,
        timestamp=payload.timestamp,
        aqi=payload.aqi,
        pm25=payload.pm25,
        pm10=payload.pm10,
        o3=payload.o3,
        co=payload.co,
        so2=payload.so2,
    )
    return obj
'''
@router.post("/") → Bu fonksiyon / yoluna POST isteği geldiğinde çalışır.
payload: AQICreate → İstek gövdesinde JSON formatında gelen veri. Pydantic modeli sayesinde doğrulanır.
db: Session = Depends(get_db) → DB oturumu alınır.
crud.upsert_air_quality(...) → Eğer kayıt varsa günceller, yoksa oluşturur (UPSERT işlemi).
Son olarak, oluşturulan veya güncellenen kayıt JSON olarak döndürülür.
'''