Bu proje NASA TEMPO + AirNow + OpenWeather verilerini kullanan, FastAPI tabanlı bir backend uygulamasıdır. Amaç: gerçek zamanlı hava kalitesi ve hava durumu verilerini çekmek, veritabanına güvenli şekilde yazmak, frontend ve ML katmanlarına servis olarak sunmak — ve aynı zamanda diskin dolmasını önleyecek şekilde büyük NETCDF granüllerini diske kaydetmeden (streaming) işlemektir.

Bu README, projeyi hiç bilmeyen birinin bile çalıştırıp anlamasını sağlayacak kadar açık ve adım adım hazırlanmıştır. Dosya/dizin yapısı, gerekli ortam değişkenleri, nasıl çalıştırılacağı, hangi komut ne yapar, sık karşılaşılan hatalar ve çözüm yolları hepsi burada.

1. Hızlı Özet (Quickstart)

Eğer Docker kullanacaksan:

Depoyu klonla / dosyaları hazırla.

.env dosyasını oluştur ve içine API anahtarlarını koy.

docker-compose up --build komutunu çalıştır.

Tarayıcıda http://127.0.0.1:8000/docs adresine git — OpenAPI dokümantasyonunu göreceksin.

Komutlar:

cp .env.example .env          # .env örneğini kopyala
# .env içindeki değişkenleri doldur (DB, API key'ler)
docker-compose up --build     # Docker ile tüm servisi ayağa kaldır


Eğer Docker istemiyorsan (lokal çalışma):

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix:
source .venv/bin/activate

pip install -r requirements.txt
# Gerekiyorsa system bağımlılıkları yükle (ör: netCDF4 için)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


Not: netCDF4 gibi bazı paketler sistem kütüphanelerine ihtiyaç duyar (libhdf5, libnetcdf). Dockerfile içinde bunlar yüklü; lokal kurulumda sorun yaşarsan README'nin ilgili bölümüne bak.

2. Proje dosya/dizin yapısı (kısa)
aq-backend/
├─ app/
│  ├─ main.py                   # FastAPI giriş noktası
│  ├─ core/
│  │  └─ config.py              # .env ve diğer ayarlar
│  ├─ db/
│  │  └─ session.py             # SQLAlchemy engine + session
│  ├─ models.py                 # ORM modelleri (Users, Locations, TempoData, ...)
│  ├─ services/
│  │  ├─ airnow_service.py
│  │  ├─ openweather_service.py
│  │  └─ tempo_service.py       # earthaccess + netCDF (streaming)
│  ├─ etl/
│  │  └─ scheduler.py           # APScheduler jobları
│  ├─ ml/
│  │  └─ predictor.py           # model yükleme (joblib)
│  └─ api/
│     └─ v1/routers/
│        ├─ aqi.py
│        └─ weather.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ .env.example
└─ README.md  <-- (bu dosya)

3. Gerekli önkoşullar (prerequisites)

Python 3.10+ (tercihen 3.11)

Docker & docker-compose (Docker kullanacaksan)

NASA Earthdata hesabı (TEMPO verilerine erişim için) — EARTHDATA_USER ve EARTHDATA_PASS

AirNow API anahtarı (AIRNOW_API_KEY) — ABD yer istasyonları için

OpenWeather API anahtarı (OPENWEATHER_API_KEY) — hava tahminleri için

MySQL veya başka bir desteklenen veritabanı; docker-compose örneği MySQL 8 kullanır.

Opsiyonel (ancak tavsiye):

scikit-learn — model eğitme/kullanma için

geojson — lokasyon/harita ile çalışacaksan

Neden Earthdata? NASA TEMPO verileri Earthdata üzerinden erişiliyor. Bazı ürünler büyük netCDF granülleri içerir; bunları disk yerine bellekten açmak (streaming) disk kullanımını azaltır.

4. Çalıştırma detayları ve .env

.env.example içeriği (kopyalayıp doldur):

DATABASE_URL=mysql+pymysql://aquser:aqpass@db:3306/airquality

EARTHDATA_USER=your_earthdata_username
EARTHDATA_PASS=your_earthdata_password

AIRNOW_API_KEY=your_airnow_key
OPENWEATHER_API_KEY=your_openweather_key


DATABASE_URL formatı:

MySQL ile örnek: mysql+pymysql://user:password@host:3306/dbname

Docker Compose içinde db hostname kullanılır (backend container içinden).

5. Uygulama bileşenlerinin açıklaması (kısa + ne işe yaradığı)

Aşağıda her ana dosyanın ne yaptığını, ana mantığını ve neden kullanıldığını açıklıyorum.

5.1 app/core/config.py

Amaç: .env veya ortam değişkenlerinden ayarları okumak.

Neden: API anahtarları ve DB bağlantılarını kod içinde sabit tutmamak için.

Örneğin settings.AIRNOW_API_KEY ile kod içinde anahtara erişiriz.

5.2 app/db/session.py

create_engine(settings.DATABASE_URL): veritabanı bağlantısı oluşturur.

SessionLocal = sessionmaker(...): request başına bir DB session almak için.

get_db() FastAPI Depends ile kullanılır; her istekten sonra session kapatılır.

5.3 app/models.py

SQLAlchemy modelleri: Users, Locations, TempoData, AirQualityData, WeatherData, Predictions.

UniqueConstraint ile aynı lokasyon/zaman çifti tekrar yazılmasın diye kısıt koyduk.

Numeric(9,6) enlem/boylam hassasiyeti için.

5.4 app/services/airnow_service.py

fetch_airnow_by_latlon(lat, lon, distance_miles): AirNow API'ye istek atar ve JSON döner.

requests.get(...).raise_for_status(): HTTP hatası varsa exception fırlatır.

5.5 app/services/openweather_service.py

fetch_onecall(lat, lon): OpenWeather OneCall 3.0 endpoint'ini çağırır.

Dönen JSON içinde current, hourly, daily bulunur.

5.6 app/services/tempo_service.py — kritik kısım (streaming)

Neden özel? TEMPO verileri netCDF formatında, büyük olabilir. Diskte biriktirirsen çok yer kaplar.

Ne yapıyoruz?

earthaccess.search_data(...) ile granülleri ararız (tarih ve bbox ile).

Her granül için earthaccess.open(uri) ile stream (indirip diske yazmadan) içerikleri okuruz.

content = fh.read() → granülün byte'larını alırız.

netCDF4.Dataset("inmemory.nc", memory=content) → netCDF içeriğini bellekten açarız.

NetCDF içindeki değişken isimleri ürüne göre farklılık gösterebilir — rehbere bak ve değişkene göre oku (ör: vertical_column_troposphere).

Lat/Lon dizisini al, istenen koordinata en yakın pikseli bul ve değeri çek.

Avantaj: diske büyük .nc dosyaları yazılmaz; sadece DB'ye ihtiyaç duyduğun küçük özetler (agregatlar) yazılır.

Önemli: ürünün değişken adları farklı olabilir — TEMPO rehberine (NASA) bakarak kullanılan değişken adını doğrula.

5.7 app/etl/scheduler.py

APScheduler ile periyodik ETL jobları tanımlanır.

Örnek: her 30 dakikada AirNow verisi çekilir, DB’ye yazılır (etl_airnow_job).

Scheduler startup event'inde çalıştırılır.

5.8 app/api/v1/routers/*

aqi.py → GET /api/v1/aq/latest?city_id=... — son kayıt.

weather.py → GET /api/v1/weather/24h?city_id=... — son 24 saat kayıtları.

Frontend bu endpoints'i kullanacak.

5.9 app/ml/predictor.py

joblib.load("app/ml/model.pkl") ile bir sklearn/xgboost vs. modelini belleğe yüklersin.

predict(features_df) ile tahmin alırsın.

Not: Modelin beklediği feature sütunlarını ETL pipeline ile birlikte tanımlayıp aynı sırada vermelisin.

6. Nasıl test edersin (adım adım)
6.1 DB’ye örnek bir location ekleme

Scheduler’ın çekebilmesi için DB’de en az bir Locations kaydı olmalı. MySQL penceresinden veya bir client ile ekle:

SQL örneği:

INSERT INTO locations (city_name, latitude, longitude) VALUES ('Istanbul', 41.015137, 28.979530);


Ayrıca Docker içindeysen:

# docker-compose ile çalışan mysql'e bağlanıp SQL çalıştırmak (örnek)
docker-compose exec db mysql -u root -prootpass -e "INSERT INTO airquality.locations (city_name, latitude, longitude) VALUES ('Istanbul', 41.015137, 28.979530);"


Not: rootpass ve DB bilgileri docker-compose.yml örneğine göre değişebilir.

6.2 Uygulamayı başlat

Docker ile:

docker-compose up --build


Lokal (Docker yoksa):

source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

6.3 Scheduler ve ETL’in çalıştığını kontrol et

Docker logları izleyin:

docker-compose logs -f backend
# veya
docker logs -f aq-backend


Arka planda çalışan APScheduler joblarının log satırlarını burada göreceksiniz (biz minimal log koyduk; daha fazla log eklemeyi tavsiye ederim).

6.4 Endpoint testleri (curl örnekleri)

Son hava kalitesi (örnek):

curl "http://127.0.0.1:8000/api/v1/aq/latest?city_id=1"


Son 24 saat hava:

curl "http://127.0.0.1:8000/api/v1/weather/24h?city_id=1"

6.5 TEMPO streaming test (manuel çağrı)

Eğer Earthdata bilgileriniz varsa Python REPL’den küçük test:

from app.services.tempo_service import find_tempo_granules, stream_and_sample_granule
# örnek arama (short_name ve tarihleri TEMPO rehberine göre doldur)
granules = find_tempo_granules("TEMPO_NO2_L3", "2025-09-13T00:00:00", "2025-09-14T00:00:00")
g = granules[0]
res = stream_and_sample_granule(g, [41.015137], [28.979530])
print(res)


Bu test, granülü indirip bellekten açıp belirttiğin koordinat için NO2 sütununu getirecek (değişken adı ürüne göre farklılık gösterebilir).

7. Hangi paketleri eklemelisin / requirements.txt notları

Proje temel requirements.txt aşağıdaki grupları içerir. Öneriler:

fastapi, uvicorn[standard] → web sunucusu

SQLAlchemy, pymysql → ORM + MySQL connector

earthaccess, netCDF4, numpy → TEMPO verileri için (stream + netCDF)

requests → AirNow / OpenWeather HTTP istekleri

apscheduler → ETL job scheduler

joblib, pandas, scikit-learn → ML model eğitme / yükleme (eğer ML geliştireceksen scikit-learn ekle)

geojson → harita / geo veri işlemleri (isteğe bağlı)

Neden scikit-learn?

Eğer modelini burada eğitmek ya da sklearn pipeline kullanmak istiyorsan gerekiyor. Eğer sadece pickle ile önceden eğitilmiş model yükleyeceksen ve model sklearn değilse, gerek olmayabilir.

Neden geojson?

Lokasyon verilerini GeoJSON formatında sunmak veya frontend ile paylaşmak istiyorsan kullanışlı.

8. TEMPO streaming — teknik detay (neden ve nasıl)

Kısa açıklama:

TEMPO ürünleri netCDF formatında ve genelde büyük dosyalar (MB'lar, bazen yüzler MB).

Çözüm: earthaccess.open(uri) ile dosyayı stream et, içeriği bellek (bytes) olarak al, netCDF4.Dataset(..., memory=content) ile bellekten aç.

Böylece diskte .nc dosyası biriktirmiyoruz; sadece çektiğimiz küçültülmüş (ör: lon/lat'e karşılık tek piksel) değerleri DB'ye kaydediyoruz.

Adımlar:

earthaccess.search_data(short_name, temporal=(start,end), bounding_box=bbox)

granülle gelen data_links()[0] ile uri al

with earthaccess.open(uri) as fh: content = fh.read()

ds = netCDF4.Dataset("inmemory.nc", memory=content)

var = ds.variables['vertical_column_troposphere'][:] (ürüne göre değişir)

lat/lon dizisi ile en yakın indeksi bul ve değeri çek

ds.close()

Neden önemli? Disk kontrolü: yarışma sürecinde disk hızla dolar; streaming ile bu problem çözülür.

9. Scheduler (APScheduler) açıklaması

BackgroundScheduler() — uygulama içinde arka planda çalışan bir scheduler.

scheduler.add_job(func, 'interval', minutes=30, id='airnow') — her 30 dakikada func fonksiyonunu çalıştırır.

start_scheduler() fonksiyonunu FastAPI startup event'inde çağırıyoruz; böylece uygulama açıldığında job'lar aktive olur.

Dikkat: Geliştirme ortamında BackgroundScheduler uygundur. Production’da daha güvenilir ve ölçeklenebilir olması için Celery + beat veya Kubernetes CronJob tercih edilebilir.

10. Disk yönetimi ve retention policy (yarışma için kritik)

Asla her .nc granülünü diske kaydetme (kayıt yapacaksan bile kısa süreli).

DB’de yalnızca:

Hourly aggregate (ör: son 24 saat için saatlik PM2.5 ortalaması)

Günlük/haftalık özet

Granül metadata (granule_id, timestamp, md5) — tekrarı engellemek için

Eğer granül saklaman gerekirse: kullan cloud object storage (S3/GS) ve lifecycle policy (7 gün sonra sil).

Örnek retention job (SQL veya Python) — her gece 30 gün öncesini sil:

DELETE FROM tempodata WHERE timestamp < NOW() - INTERVAL 30 DAY;
DELETE FROM airqualitydata WHERE timestamp < NOW() - INTERVAL 60 DAY;

11. Güvenlik & prod notları

.env içindeki anahtarları asla repoya koyma.

CORS ayarında allow_origins=["*"] geliştirme için kabul edilir ama prod’da kesinlikle domain whitelist yap.

DB şifresini ve API anahtarlarını çevresel değişkenlerde tut.

Rate limits: AirNow ve OpenWeather limitlerini kontrol et; aşarsan IP/anahtar engellenebilir.

Audit log: ETL jobları için hata loglamayı arttır, retry mantığı ekle.

12. Sık karşılaşılan hatalar & çözümleri
1) netCDF4 pip install hata veriyor (özellikle Windows)

Çözüm: sistem paketleri eksik. Dockerfile içinde libhdf5-dev ve libnetcdf-dev yükleniyor. Lokal Linux’ta:

sudo apt-get update
sudo apt-get install -y libhdf5-dev libnetcdf-dev
pip install netCDF4


Windows için conda kullanmak en pratik yol:

conda create -n aq python=3.10
conda activate aq
conda install -c conda-forge netCDF4 earthaccess numpy
pip install -r requirements.txt  # diğer paketler

2) Earthdata login hatası / authentication problem

earthaccess genelde interaktif earthaccess login veya earthaccess.login(username, password) ile çalışır.

İlkkez çalıştırırken terminalde earthaccess login komutunu verip credential’ı kaydetmeyi dene.

Eğer 2FA varsa veya kurum hesabı gerekiyorsa Earthdata belgelerine bak.

3) AirNow boş liste dönüyor

AirNow sadece ABD içindeki yer istasyonlarını kapsar. Lokasyon ABD değilse sonuç boş gelebilir.

Parametre distance'ı arttırmayı dene veya başka veri kaynağı kullan (OpenAQ, PurpleAir vb).

4) Scheduler jobları çalışmıyor / logs yok

docker-compose logs -f backend ile logları izle.

Localde uvicorn ile çalıştırırken DEBUG log ekleyip start_scheduler() çağrıldığını doğrula.

13. ML entegrasyonu — kısa yol haritası

Modeli eğit (jupyter/Colab) — feature spec oluştur (ör: last_24h_avg_pm25, last_3h_max_o3, temp, humidity).

Kaydet: joblib.dump(model, "app/ml/model.pkl")

app/ml/predictor.py dosyası model yükleme ve predict fonksiyonunu tutar.

Bir endpoint yaz (ör: POST /api/v1/predict?city_id=) — şu adımları uygular:

DB’den son 24h verileri çek

Öznitelik vektörünü oluştur (pandas DataFrame)

predictor.predict(df) çağır

Predictions tablosuna kaydet

Frontend prediction sonuçlarını gösterir veya alarm tetikler.

Örnek endpoint (basit):

@router.post("/predict")
def predict(city_id: int, db: Session = Depends(get_db)):
    # 1) DB'den feature verilerini al
    # 2) features_df = ...
    preds = predictor.predict(features_df)
    # 3) sonuc DB'ye kaydet
    return {"predicted_aqi": int(preds[0])}

14. Dosya bazlı satır satır açıklama vs. README farkı

Zaten projedeki her dosyada satır satır yorumlar (inline # ...) ekledim. README burada daha çok kavramsal rehber ve çalıştırma + test + hata çözüm odaklı.

Kodun içindeki tempo_service.py bölümünde earthaccess.open() + netCDF4.Dataset(..., memory=content) akışı doğrudan gösterilmiştir — aynısını kullanman yeterli.

15. Ek notlar / tavsiyeler (yarışma için)

İlk öncelik: TEMPO streaming örneğini çalıştırıp, bir lokasyon için doğru değer çektiğine emin ol. Bu disk sorununu çözecek.

İkinci öncelik: Scheduler’ı güvenilir hale getir — job retry, eksik veri detection, loglama.

Üçüncü öncelik: Frontend ile API sözleşmesini netleştir: (endpoint input/output JSON formatları).

Dördüncü: Prod ortam için Alembic migration ve Docker image CI/CD pipeline oluştur.

16. Sıkça Sorulan Sorular (FAQ)

S: Earthdata olmadan TEMPO çalışır mı?
A: Hayır — TEMPO ürünlerine erişim için Earthdata hesabı gerekir.

S: AirNow dünya çapında veri verir mi?
A: Hayır, AirNow temelde ABD merkezlidir. Diğer ülkeler için OpenAQ, PurpleAir vb. kaynaklar kullanılmalı.

S: Neden veriyi diske kaydetmiyoruz?
A: NetCDF granülleri çok büyük olabilir ve yarışma/takım çalışmasında diski doldurur; streaming ile sadece ihtiyacımız olan piksel/özet değerini alıp kaydederiz.

17. Son adım — ne yapmanı öneririm şimdi

.env’i doldur ve Docker ile projeyi ayağa kaldır: docker-compose up --build

Locations tablosuna en az bir kayıt ekle (örnek İstanbul).

docker-compose logs -f backend ile ETL loglarını izle.

curl "http://127.0.0.1:8000/api/v1/aq/latest?city_id=1" ile endpoint’i test et.

TEMPO testini Python REPL’de çalıştır — find_tempo_granules ve stream_and_sample_granule ile.

18. İleriye dönük iyileştirmeler (öneriler)

Alembic migration konfigürasyonu ekle (DB değişiklikleri için).

ETL joblarını daha dayanıklı yapmak için Celery + Redis kullan.

Granül metadata tablosu ekle: granule_id, product, date, md5, processed_bool — böylece tekrar işleme engellenir.

Monitoring/metrics (Prometheus / Grafana).

Rate-limit ve throttling için backoff-stratejisi.

19. Yardım / iletişim

Burada anlattığım adımları uygularsan büyük ihtimalle çalışacaktır. Hala hata alırsan bana:

Hangi adımı yaptığını,

Aldığın hata mesajını (tam çıktısı),

.env içeriğinden gizli bilgileri çıkarıp (anahtarlar değil) DB connection string formatını paylaş,
gönder — hatayı beraber çözelim.