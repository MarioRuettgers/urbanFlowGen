import cdsapi
import os

# =============================
# User-defined parameters
# =============================
year = "2023"  # Year as a string
area = [39.5, 124.0, 33.0, 131.0]  # [North (max. Lat.), West (min. Long.), South (min. Lat.), East (max. Long.)]
target_directory = "./era5"  # Directory to save the file

# Create directory if it doesn't exist
os.makedirs(target_directory, exist_ok=True)

# Filename with year in it
output_file = os.path.join(target_directory, f"era5_{year}.grib")

# =============================
# ERA5 Data Request
# =============================
dataset = "reanalysis-era5-single-levels"

request = {
    "product_type": ["reanalysis"],
    "variable": [
        "10m_u_component_of_neutral_wind",
        "10m_v_component_of_neutral_wind"
    ],
    "year": [year],
    "month": [f"{m:02d}" for m in range(1, 13)],
    "day": [f"{d:02d}" for d in range(1, 32)],
    "time": [f"{h:02d}:00" for h in range(24)],
    "data_format": "grib",
    "download_format": "unarchived",
    "area": area  # [North, West, South, East]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download(output_file)

