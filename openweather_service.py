# app/services/openweather_service.py
import requests
'''
requests kütüphanesini import ediyoruz. Bu kütüphane, Python’da HTTP GET/POST istekleri yapmak için kullanılır.
'''
from app.core.config import settings
'''
Kendi projemizdeki settings objesini içe aktarıyoruz.

settings, .env dosyasında tanımlı API key gibi ortam değişkenlerini okuyor.

Burada OPENWEATHER_API_KEY kullanılacak.
'''

ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"
'''
OpenWeather’ın One Call 3.0 endpoint URL’si.

Bu API, belirli bir enlem/boylam için anlık hava durumu, saatlik tahmin ve günlük tahmin verilerini döner.
'''

def fetch_onecall(lat: float, lon: float, units: str = "metric"):
    '''
    fetch_onecall adında bir fonksiyon tanımlıyoruz.

    Parametreler:

    lat → enlem (float)

    lon → boylam (float)

    units → ölçü birimi, varsayılan "metric" (°C, m/s). "imperial" seçilirse °F gibi değerler döner.
    '''
    """
    OpenWeather One Call 3.0 çağrısı.
    Dönüş: JSON (current, hourly, daily)
    '''
    Bu fonksiyon OpenWeather One Call API’sine istek atar.

Dönüş değeri JSON formatında olur:

current (anlık hava)

hourly (saatlik tahmin)

daily (günlük tahmin).
    '''
    """
    params = {
        "lat": lat,
        "lon": lon,
        "units": units,
        "appid": settings.OPENWEATHER_API_KEY,
    }
    '''
    API’ye gönderilecek query parametrelerini hazırlıyoruz:

"lat" → enlem

"lon" → boylam

"units" → metrik/imperial

"appid" → OpenWeather API anahtarı ( .env dosyasından geliyor).
    '''
    r = requests.get(ONECALL_URL, params=params, timeout=15)
    '''
    GET isteği gönderiyoruz.

URL → ONECALL_URL

Parametreler → params sözlüğü

timeout=15 → 15 saniyeden uzun sürerse hata fırlat.
    '''
    r.raise_for_status()
    '''
    Eğer yanıtın HTTP status kodu 200 dışı ise (örn. 401 Unauthorized, 404 Not Found, 500 Server Error), burada hata (HTTPError) fırlatılır.
Bu sayede kod sessizce başarısız olmaz.
    '''
    return r.json()
'''
Dönen cevabı JSON olarak parse edip fonksiyon çıktısı olarak döndürüyoruz.

Yani bu fonksiyonu çağıran kişi doğrudan bir Python dict/list yapısı alır.

Bu fonksiyon verilen lat, lon koordinatları için OpenWeather One Call 3.0 API’sinden hava durumu verisi alıyor ve JSON döndürüyor.
'''
