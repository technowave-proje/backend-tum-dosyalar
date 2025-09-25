# app/db/session.py
from sqlalchemy import create_engine
'''
create_engine → SQLAlchemy’nin veritabanına bağlanmak için kullandığı fonksiyon.

İçine bir veritabanı URL’si veriyoruz (mysql://..., sqlite:///... gibi).

Engine, uygulamanın DB ile konuşmasını sağlayan temel nesne.
'''
from sqlalchemy.orm import sessionmaker, declarative_base
'''
sessionmaker → DB ile etkileşim için Session nesneleri oluşturur.

declarative_base → ORM modellerini (tablolara karşılık gelen Python sınıfları) tanımlamak için bir temel sınıf sağlar.

Yani Base = declarative_base() yaptıktan sonra tüm modeller Base’den miras alır.
'''
from app.core.config import settings
'''
Bir önceki dosyada tanımladığımız settings nesnesini buraya import ediyoruz.

Böylece .env dosyasındaki DATABASE_URL ayarını buradan okuyabiliyoruz.

Yani DB bağlantı adresi dinamik olarak .env’den geliyor.
'''

# Create SQLAlchemy engine with pool_pre_ping to avoid stale connections
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
'''
engine oluşturuluyor → settings.DATABASE_URL kullanılarak veritabanına bağlanıyor.

pool_pre_ping=True: Uzun süre kullanılmamış bağlantıların ölüp ölmediğini test eder.

Eğer bağlantı düşmüşse otomatik olarak yeniler.

Bu sayede “stale connection” (bozuk bağlantı) hataları önlenir.
'''

# create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
'''
SessionLocal adında bir sessionmaker nesnesi oluşturuluyor.

Parametreler:

autocommit=False: SQL işlemlerinin otomatik commit edilmemesi için. (Yani biz db.commit() demeden işlem kalıcı olmaz.)

autoflush=False: DB’ye her değişiklikte otomatik flush yapılmaz, kontrol bizde olur.

bind=engine: Bu session, yukarıda tanımladığımız engine ile veritabanına bağlanacak.

SessionLocal() çağırarak bir veritabanı oturumu (session) açıyoruz.
'''

Base = declarative_base()
'''
ORM modellerinin (tabloların) türetileceği temel sınıf.

Tüm DB tablolarımız için yazacağımız modeller (User, Weather, City vs.) bu Base’den miras alacak:

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
'''

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''
FastAPI için DB oturumu sağlayan dependency (bağımlılık).

Çalışma şekli:

db = SessionLocal() → yeni bir veritabanı oturumu açılır.

yield db → endpoint içinde bu session kullanılır.

Endpoint işi bitince finally bloğu çalışır ve db.close() ile bağlantı kapatılır.

FastAPI’de Depends(get_db) yazarak DB session’ı otomatik olarak endpoint fonksiyonuna enjekte edebiliriz.

✅ Özetle bu dosya:

engine ile veritabanına bağlanıyor.

SessionLocal ile session sınıfı oluşturuyor.

Base ile modeller için temel sınıf veriyor.

get_db() ile FastAPI endpointlerine güvenli DB bağlantısı sağlıyor.
'''
