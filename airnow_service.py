# app/services/airnow_service.py
import requests
'''
requests → HTTP istekleri yapmak için kullanılan popüler Python kütüphanesi.

Burada AirNow API’sine GET isteği göndermek için kullanılıyor.
'''
from app.core.config import settings
'''
Daha önce tanımlanan settings nesnesini içe aktarıyor.

Bunun sayesinde .env dosyasındaki AIRNOW_API_KEY (AirNow API anahtarı) kullanılabiliyor.

Yani API’ye erişim için gerekli kimlik doğrulama burada ayarlanıyor.
'''

BASE = "https://www.airnowapi.org/aq/observation/latLong/current/"
'''
AirNow API’sinin temel URL adresi.

Bu endpoint, verilen enlem/boylama göre anlık hava kalitesi gözlemlerini (current observations) döndürüyor.
'''

def fetch_airnow_by_latlon(lat: float, lon: float, distance_miles: int = 25):
    """
    AirNow'dan o anki gözlemleri çek.
    Dönüş: parsed JSON listesi (her öğe farklı bir ParameterName: PM2.5, O3, vb.)
    Bir fonksiyon tanımlıyoruz: fetch_airnow_by_latlon.

Parametreler:

lat: float → Enlem (latitude).

lon: float → Boylam (longitude).

distance_miles: int = 25 → Varsayılan arama yarıçapı, 25 mil.

Yani verilen koordinata 25 mil mesafedeki hava kalitesi istasyonlarını kapsar.
    """
    params = {
        "format": "application/json",
        "latitude": lat,
        "longitude": lon,
        "distance": distance_miles,
        "API_KEY": settings.AIRNOW_API_KEY,
    }
    '''
    API çağrısı için kullanılacak parametreler (query string) hazırlanıyor:

"format": "application/json" → JSON formatında cevap istiyoruz.

"latitude": lat → Kullanıcıdan alınan enlem değeri.

"longitude": lon → Kullanıcıdan alınan boylam değeri.

"distance": distance_miles → Varsayılan olarak 25 mil arama yarıçapı.

"API_KEY": settings.AIRNOW_API_KEY → AirNow API anahtarı (.env dosyasından geliyor).
    '''
    # HTTP GET isteği yapıyoruz; requests basit ve yeterli
    resp = requests.get(BASE, params=params, timeout=15)
    '''
    requests.get(...) ile AirNow API’sine HTTP GET isteği gönderiliyor.

BASE: Temel API URL’si.

params=params: Yukarıda hazırladığımız parametreler URL’ye ekleniyor.

timeout=15: Eğer API 15 saniye içinde yanıt vermezse hata fırlatılır.

Dönen cevap resp değişkeninde saklanır.
    '''
    resp.raise_for_status()
    '''
    Eğer yanıt bir hata kodu içeriyorsa (400, 401, 500 gibi), bir exception fırlatılır.

Bu sayede “sessizce başarısız olma” yerine doğrudan hata alırız.
    '''
    return resp.json()
'''
API’den gelen cevap JSON formatında parse edilip döndürülür.

Dönen değer: Python listesi/dictionary (AirNow’un gönderdiği verilere bağlı).

Örneğin:

[
  {"ParameterName": "PM2.5", "AQI": 42, "Category": {"Name": "Good"}},
  {"ParameterName": "O3", "AQI": 55, "Category": {"Name": "Moderate"}}
]
✅ Özet:

Bu servis fonksiyonu, AirNow API’sine lat/lon ile istek atar.

JSON formatında anlık hava kalitesi ölçümlerini alır.

Dönen her öğe → bir parametrenin ölçümü (PM2.5, O3, vs.).
'''
