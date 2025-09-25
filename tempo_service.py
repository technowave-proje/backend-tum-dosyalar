import datetime as dt
from datetime import timezone
import os
from decimal import Decimal
import mysql.connector
from harmony import BBox, Client, Collection, Request
import xarray as xr
from netCDF4 import Dataset
import numpy as np
from dotenv import load_dotenv

# --------------------------
# .env dosyasını yükle
# --------------------------
load_dotenv()
USERNAME = os.getenv("EARTHDATA_USER")
PASSWORD = os.getenv("EARTHDATA_PASS")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

# --------------------------
# MySQL config
# --------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": MYSQL_PASSWORD,
    "database": "nasa_project"
}

# --------------------------
# Harmony client
# --------------------------
harmony_client = Client(auth=(USERNAME, PASSWORD))

# --------------------------
# L3 koleksiyonları ve gazlar
# --------------------------
gases = {
    "no2": [("NO2_L3", "C3685896708-LARC_CLOUD")],
    "o3": [("O3_L3", "C2930764281-LARC_CLOUD")],
    "hcho": [("HCHO_L3", "C3685897141-LARC_CLOUD")]
}

# --------------------------
# Decimal veya masked array -> float
# --------------------------
def safe_float(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, np.ma.MaskedArray):
        return float(value.mean())
    return float(value)

# --------------------------
# Dataset’i güvenli aç
# --------------------------
def open_dataset_safe(file_path):
    for engine in ["netcdf4", "h5netcdf"]:
        try:
            ds = xr.open_dataset(file_path, engine=engine)
            return ds
        except Exception:
            continue
    try:
        ds = Dataset(file_path, "r")
        return ds
    except Exception:
        return None

# --------------------------
# Ortalama değer hesapla
# --------------------------
def get_mean_from_dataset(ds, var_name):
    try:
        if isinstance(ds, xr.Dataset):
            if "product" in ds:
                data_array = ds["product"][var_name]
                if "qa_value" in ds["product"]:
                    quality_flags = ds["product"]["qa_value"]
                    good_array = data_array.where(quality_flags == 0)
                else:
                    good_array = data_array
            else:
                data_array = ds[var_name]
                good_array = data_array
            return safe_float(good_array.mean().values)
        elif isinstance(ds, Dataset):
            data_array = ds.variables[var_name][:]
            return safe_float(np.mean(data_array))
    except Exception as e:
        print(f"⚠ Hata get_mean_from_dataset: {e}")
        return None

# --------------------------
# Tek location için veri çek
# --------------------------
def fetch_for_location(loc, start_time, stop_time, bbox_buffer=0.25):
    loc_id = loc["location_id"]
    lat = loc["latitude"]
    lon = loc["longitude"]

    data_to_insert = {
        "timestamp": stop_time,
        "location_id": loc_id,
        "o3": None,
        "no2": None,
        "hcho": None,
        "so2": None,
        "co": None,
        "aerosol_index": None
    }

    for gas_key, gas_list in gases.items():
        for gas_name, collection_id in gas_list:
            try:
                request = Request(
                    collection=Collection(id=collection_id),
                    temporal={"start": start_time, "stop": stop_time},
                    spatial=BBox(lon-bbox_buffer, lat-bbox_buffer, lon+bbox_buffer, lat+bbox_buffer),
                    output_format="netcdf"  # netCDF formatında indir
                )
                job_id = harmony_client.submit(request)
                print(f"Job submit edildi: {job_id}")
                harmony_client.wait_for_processing(job_id)
                results = list(harmony_client.download_all(job_id))
                print(f"Dosya sayısı: {len(results)} -> {results}")

                for file_path in results:
                    ds = open_dataset_safe(file_path)
                    if ds is None:
                        print(f"⚠ Dataset açılamadı: {file_path}")
                        continue

                    var_candidates = []
                    if isinstance(ds, xr.Dataset):
                        if "product" in ds:
                            var_candidates = [v for v in ds["product"].data_vars if gas_key in v.lower()]
                        else:
                            var_candidates = [v for v in ds.data_vars if gas_key in v.lower()]
                    elif isinstance(ds, Dataset):
                        var_candidates = [v for v in ds.variables if gas_key in v.lower()]

                    if not var_candidates:
                        print(f"⚠ Değişken bulunamadı: {gas_key}")
                        continue

                    mean_val = get_mean_from_dataset(ds, var_candidates[0])
                    if mean_val is not None:
                        # Örnek düzeltmeler
                        if gas_key == "no2":
                            mean_val -= 5.0
                        elif gas_key == "o3":
                            mean_val -= 2.0
                        elif gas_key == "hcho":
                            mean_val -= 1.0
                        data_to_insert[gas_key] = mean_val
                        break
            except Exception as e:
                print(f"⚠ {gas_name} hata (location_id={loc_id}): {e}")
                continue
    print(f"Location {loc_id} için veri: {data_to_insert}")
    return data_to_insert

# --------------------------
# DB’ye insert
# --------------------------
def insert_to_db(row):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO tempodata (timestamp, location_id, o3, no2, hcho, so2, co, aerosol_index)
        VALUES (%(timestamp)s, %(location_id)s, %(o3)s, %(no2)s, %(hcho)s, %(so2)s, %(co)s, %(aerosol_index)s)
        ON DUPLICATE KEY UPDATE 
            o3=VALUES(o3), no2=VALUES(no2), hcho=VALUES(hcho),
            so2=VALUES(so2), co=VALUES(co), aerosol_index=VALUES(aerosol_index)
    """
    for key in ["o3","no2","hcho","so2","co","aerosol_index"]:
        row[key] = safe_float(row[key])
    cursor.execute(insert_query, row)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Veri DB’ye yazıldı: location {row['location_id']}")

# --------------------------
# Ana çalıştırma
# --------------------------
if __name__ == "__main__":
    test_loc = {"location_id": 1, "latitude": 19.4, "longitude": -99.1}  # Örnek nokta
    start_time = dt.datetime.now(timezone.utc) - dt.timedelta(days=1)
    stop_time = dt.datetime.now(timezone.utc)

    result = fetch_for_location(test_loc, start_time, stop_time)
    insert_to_db(result)
