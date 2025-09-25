# app/api/v1/routers/predict.py
from fastapi import APIRouter, Depends, HTTPException
'''
FastAPI kütüphanesinden üç şeyi içe aktarıyoruz:
APIRouter → Endpoint’leri bir router altında organize etmek için kullanılır. Modüler bir yapı sağlar.
Depends → Dependency Injection (bağımlılık yönetimi) için. Örneğin DB oturumu veya başka servisleri endpoint’e otomatik vermek için.
HTTPException → API’de hata durumlarını HTTP kodu ile belirtmek için. Örneğin 400 veya 404 hatası döndürmek için.
'''
from sqlalchemy.orm import Session
'''
SQLAlchemy’nin Session sınıfı.
DB oturumunu temsil eder, sorgular, ekleme/güncelleme işlemleri bu oturum üzerinden yapılır.
'''
from app.db.session import get_db
'''
get_db → Veritabanı oturumu sağlayan fonksiyon.
Depends(get_db) ile endpoint’e DB oturumu olarak aktarılır.
'''
from app.ml.predictor import Predictor
'''
ML (Machine Learning) tahminlerini yapan sınıfı içe aktarıyoruz.
Bu sınıf muhtemelen eğitimli bir model içeriyor ve predict_aqi fonksiyonu ile AQI tahmini yapıyor.
'''

router = APIRouter()
'''
Yeni bir FastAPI router oluşturuyoruz.
Bu router’a endpoint ekleyip, daha sonra ana FastAPI uygulamasına (app.include_router(router)) bağlayacağız.
'''

@router.get("/{location_id}")
# Bu decorator endpoint’i tanımlar: /some_location_id yoluna gelen GET isteği bu fonksiyonu tetikler.
# location_id URL parametresi olarak gelir.
def predict(location_id: int, db: Session = Depends(get_db)):
    '''
    Endpoint fonksiyonun başı.
    Parametreler:
    location_id: int → Tahmin yapmak istediğimiz konum ID’si.
    db: Session = Depends(get_db) → FastAPI otomatik olarak DB oturumunu sağlar.
    '''
    predictor = Predictor()
    '''
    Predictor sınıfının bir örneğini oluşturuyoruz.
    Bu örnek modelin tahmin yapmasını sağlar. Her çağrıda yeni bir örnek yaratıyoruz (stateless kullanım).
    '''
    res = predictor.predict_aqi(db, location_id)
    '''
    predict_aqi fonksiyonu çağrılıyor.
    Parametreler:
    db → DB oturumu, model geçmiş verileri veya diğer girdileri çekmek için.
    location_id → Hangi konum için tahmin yapılacak.
    Fonksiyonun döndürdüğü res, genellikle bir dict:
    {"aqi_predicted": 45, "timestamp": datetime.now()}
    Eğer bir hata oluşursa, dict içinde "error" anahtarı olabilir.
    '''
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res["error"])
    '''
    Tahmin sırasında bir hata oluşursa:
    res bir dict ve "error" anahtarı varsa, HTTP 400 Bad Request hatası döndür.
    detail=res["error"] → Hata mesajını yanıt olarak API’ye gönderir.
    '''
    return res
'''
Tahmin başarılıysa res JSON olarak döndürülür.
FastAPI dict’i otomatik JSON’a çevirir. Örnek çıktı:
{
  "aqi_predicted": 45,
  "timestamp": "2025-09-21T16:30:00"
}

GET isteği gelir → /123 gibi bir location_id ile.
DB oturumu oluşturulur (get_db).
Predictor sınıfı örneği oluşturulur.
predict_aqi çağrılır → DB ve location_id ile tahmin yapılır.
Hata varsa HTTP 400 ile döner, yoksa tahmin sonucu JSON olarak döner.

'''