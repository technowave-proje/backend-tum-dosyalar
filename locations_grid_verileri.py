import numpy as np
import mysql.connector
from sqlalchemy.engine.url import make_url
from app.core.config import settings  # config.py içindeki ayarları kullanıyoruz

# 🔹 DATABASE_URL'i parçala
url = make_url(settings.DATABASE_URL)
db_host = url.host
db_user = url.username
db_password = url.password
db_name = url.database

# 🔹 Grid sınırları (Kuzey Amerika)
lat_min, lat_max = 14, 72
lon_min, lon_max = -170, -50
step = 0.25

lats = np.arange(lat_min, lat_max + step, step)
lons = np.arange(lon_min, lon_max + step, step)

# 🔹 MySQL bağlantısı
conn = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = conn.cursor()

# 🔹 Locations tablosunu doldur
insert_query = """
INSERT IGNORE INTO locations (latitude, longitude, grid_name)
VALUES (%s, %s, %s)
"""

count = 0
for lat in lats:
    for lon in lons:
        grid_name = f"Grid_{lat:.2f}_{lon:.2f}"
        cursor.execute(insert_query, (float(lat), float(lon), grid_name))
        count += 1

conn.commit()
cursor.close()
conn.close()

print(f"✅ Locations tablosuna {count} grid noktası eklendi.")
