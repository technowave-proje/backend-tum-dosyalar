from netCDF4 import Dataset

# Dosyanı aç
dataset = Dataset("111284681_TEMPO_NO2_L2_NRT_V02_20250922T164052Z_S007G07_subsetted.nc" \
"", "r")

# Dosya hakkında genel bilgi
print(dataset)