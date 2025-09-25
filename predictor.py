#app\ml\predictor
import joblib
'''
joblib → Python’da makine öğrenmesi modellerini (scikit-learn gibi) dosyaya kaydetmek ve dosyadan yüklemek için kullanılan bir kütüphane.

Burada, eğitilmiş AQI tahmin modelini .pkl dosyasından yüklemek için kullanılıyor.
'''
import os
'''
os → İşletim sistemi ile ilgili işlemler için Python’un standart kütüphanesi.

Burada dosya yolu ve ortam değişkenleri (environment variables) yönetmek için kullanılıyor.
'''
from app import crud
'''
Projede yazılmış olan CRUD fonksiyonlarını içe aktarıyor.

Buradan crud.get_last_24h_air_quality fonksiyonunu kullanarak son 24 saatlik AQI verilerini DB’den alıyoruz.
'''

MODEL_PATH = os.getenv("ML_MODEL_DIR", "app/ml/models/aqi_model.pkl")
'''
Model dosyasının yolu ayarlanıyor.

os.getenv("ML_MODEL_DIR", "app/ml/models/aqi_model.pkl"):

Eğer .env veya sistemde ML_MODEL_DIR adında bir ortam değişkeni varsa, onu kullanır.

Yoksa varsayılan olarak "app/ml/models/aqi_model.pkl" yolunu alır.

Bu dosya, eğitilmiş modelin pickle (.pkl) formatında saklandığı yer.
'''

class Predictor:
    '''
    Tahmin işlemlerini kapsayan bir sınıf tanımlıyoruz.

    Bu sınıf, modeli yükleyip tahmin yapma işlevlerini içeriyor.
    '''
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        self.model = joblib.load(MODEL_PATH)
        '''
        Kurucu metod (__init__): Sınıftan Predictor() nesnesi oluşturulunca otomatik çalışır.

        if not os.path.exists(MODEL_PATH): Eğer model dosyası bulunmazsa → FileNotFoundError hatası fırlatır.

        self.model = joblib.load(MODEL_PATH): Model dosyası bulunduysa RAM’e yüklenir.

        Artık self.model.predict(...) ile tahmin yapılabilir.
        '''

    def predict_aqi(self, db, location_id: int):
        '''
        predict_aqi → Belirli bir lokasyon için hava kalitesi tahmini yapan metod.

        Parametreler:

        db: Veritabanı oturumu (FastAPI’de Depends(get_db) ile geliyor).

        location_id: Hangi konum için tahmin yapılacağını belirler.
        '''
        data = crud.get_last_24h_air_quality(db, location_id)
        '''
        Verilen location_id için son 24 saatteki hava kalitesi verilerini DB’den çekiyor.

        Bu veri listesi data içinde saklanıyor.
        '''
        if not data:
            return {"error": "Yeterli veri yok"}
        '''
        Eğer hiç veri bulunmazsa, tahmin yapılamaz.

        Bu durumda bir hata mesajı döndürülüyor: "Yeterli veri yok".
        '''

        # example feature: mean of aqi values (modify with real fe)
        features = [record.aqi for record in data if record.aqi is not None]
        '''
        Burada basit bir özellik çıkarımı (feature extraction) yapılıyor.

        data içindeki her kaydın aqi değeri alınıyor.

        Eğer aqi boş değilse (None değilse), listeye ekleniyor.

        Sonuç: features listesi → son 24 saatte ölçülmüş AQI değerleri.
        '''
        if not features:
            return {"error": "Yeterli sayıda AQI ölçümü yok"}
        '''
        Eğer hiç geçerli AQI ölçümü yoksa, tahmin yapılamaz.

        Bu durumda "Yeterli sayıda AQI ölçümü yok" hatası döndürülür.
        '''
        avg = sum(features) / len(features)
        '''
        features listesindeki AQI değerlerinin ortalaması alınıyor.

        Burada örnek olarak ortalama değer modelin girdisi olarak kullanılıyor.

        Gerçekte, daha fazla özellik (PM2.5, PM10, sıcaklık, nem vs.) eklenebilir.
        '''
        prediction = self.model.predict([[avg]])
        '''
        self.model.predict(...): Yüklenen model ile tahmin yapar.

        Modelin beklediği girdi formatı → 2 boyutlu bir liste ([[avg]]).

        Yani tek bir örnek, tek bir özellik: ortalama AQI.

        Çıktı prediction değişkenine kaydedilir (örn: [75.3] gibi).
        '''
        return {"location_id": location_id, "predicted_aqi": float(prediction[0])}
    
    '''
    Tahmin sonucu bir JSON dict olarak döndürülüyor.

    İçinde:

    location_id: Hangi lokasyon için tahmin yapıldığını gösterir.

    predicted_aqi: Tahmin edilen AQI değeri (float’a çevrilmiş).

    ✅ Özet:

    Bu sınıf, .pkl dosyasındaki modeli yükler.

    Son 24 saatlik AQI verilerini DB’den alır.

    Ortalama AQI’yi model girdisi olarak kullanır.

    Tahmin edilen değeri JSON olarak döndürür.
    '''