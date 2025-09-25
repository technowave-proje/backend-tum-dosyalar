# app\etl\schedular
from apscheduler.schedulers.background import BackgroundScheduler
'''
apscheduler → “Advanced Python Scheduler” kütüphanesi, Python’da zamanlanmış görevler çalıştırmak için kullanılır.

BackgroundScheduler → Arka planda çalışan bir zamanlayıcıdır.

Uygulamanız çalışırken, başka işlerin yanında belirlediğiniz zamanlarda fonksiyonları tetikleyebilir.

Örn: Her saat başı veri çekmek gibi.
'''
from app.services import tempo_service
'''
tempo_service adındaki servis dosyasını içe aktarıyoruz.

Bu dosyada TEMPO uydusundan veri çekip DB’ye kaydeden fonksiyonlar bulunuyor.

Burada kullanacağımız fonksiyon: fetch_and_save_all.
'''
from app.db.session import SessionLocal
'''
Daha önce öğrendiğimiz SessionLocal sınıfını içe aktarıyoruz.

SessionLocal() → yeni bir veritabanı oturumu (session) açmamızı sağlar.

Böylece tempo_service çalışırken DB’ye yazabileceğiz.
'''

def scheduled_job():
    """Scheduler tetiklendiğinde TEMPO verisini DB'ye kaydeder."""
    '''
    Bu fonksiyon, scheduler tarafından çağrılacak iş.

    Yani her tetiklendiğinde TEMPO verilerini çekecek ve DB’ye kaydedecek.
    '''
    db = SessionLocal()
    '''
    Yeni bir veritabanı oturumu açıyoruz.

    Bu oturum tempo_service’in DB üzerinde çalışabilmesi için gerekli.
    '''
    try:
        tempo_service.fetch_and_save_all(db, "2025-09-01", "2025-09-02")  # İstediğin tarih aralığı
        '''
        tempo_service.fetch_and_save_all(...) → belirtilen tarih aralığındaki TEMPO verilerini çekiyor ve DB’ye kaydediyor.

        Burada test amaçlı "2025-09-01" ile "2025-09-02" sabit girilmiş.

        Gerçekte bu tarihleri dinamik hale getirebilirsin (örn: “bugün” veya “son 24 saat”).
        '''
    finally:
        db.close()
        '''
        Ne olursa olsun (başarı veya hata), açılan DB oturumu kapatılıyor.

        Bu, bağlantıların açık kalmaması için önemli.
        '''

def start_scheduler():
    """BackgroundScheduler başlatılır, 1 saatte bir veri çek."""
    '''
    start_scheduler fonksiyonu → Scheduler’ı başlatmak için yazılmış.

    Uygulama açıldığında bu fonksiyon çağrılırsa, veri çekme işlemleri otomatik başlayacak.
    '''
    scheduler = BackgroundScheduler()
    '''
    BackgroundScheduler nesnesi oluşturuluyor.

    Bu scheduler uygulamanın arka planında çalışacak.
    '''
    scheduler.add_job(scheduled_job, 'interval', hours=1)
    '''
    add_job → Scheduler’a bir iş ekler.

    scheduled_job: Hangi fonksiyonun çalıştırılacağı.

    'interval': Zamanlama türü → belirli aralıklarla çalıştır anlamına gelir.

    hours=1: Bu iş her 1 saatte bir tetiklenecek.

    Yani her saatte scheduled_job() çağrılır → TEMPO verileri çekilir.
    '''
    scheduler.start()
    '''
    Scheduler başlatılıyor.

    Artık arka planda her 1 saatte bir otomatik veri çekmeye başlayacak.

    scheduled_job → DB oturumu açar, tempo_service ile TEMPO verilerini çeker ve DB’ye kaydeder.

    start_scheduler → Arka planda çalışan bir zamanlayıcı başlatır, bu işlevi her 1 saatte bir tetikler.
    '''
