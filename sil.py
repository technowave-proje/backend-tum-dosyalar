from dotenv import load_dotenv
import os

load_dotenv(r"C:\Users\serra\OneDrive - duzce.edu.tr\nasa_projesi\BACKEND\nasa-aqi-backend\app\services\.env")

USERNAME = os.getenv("EARTHDATA_USER")
PASSWORD = os.getenv("EARTHDATA_PASS")

print("USERNAME:", USERNAME)
print("PASSWORD:", PASSWORD)
