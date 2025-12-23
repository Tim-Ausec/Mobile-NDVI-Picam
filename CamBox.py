# === IMPORT STANDARD LIBRARIES ===
import time
import datetime
import os
import numpy as np
import cv2

# === PICAMERA2 (FOR DUAL CAMERA SETUP) ===
from picamera2 import Picamera2

# === RASTERIO FOR GEOTIFF CREATION ===
import rasterio
from rasterio.transform import Affine

# === TRY TO IMPORT GPS MODULES ===
try:
    import serial
    import pynmea2
    GPS_AVAILABLE = True
except ImportError:
    print("[INFO] GPS libraries not found — using fake GPS for testing.")
    GPS_AVAILABLE = False

# === GENERAL CONFIGURATION ===
OUTPUT_DIR = "/home/agrovolo/Desktop/ndvi_captures"
PIXEL_SIZE = 1.0
CRS = "EPSG:4326"
IMAGE_SIZE = (640, 480)
CAPTURE_INTERVAL = 5  # seconds between captures
MAX_TIME_MIN = 5 # total minutes for program execution

# === GPS CONFIGURATION ===
if GPS_AVAILABLE:
    GPS_PORT = "/dev/serial0"
    GPS_BAUD = 9600
    try:
        gps_serial = serial.Serial(GPS_PORT, GPS_BAUD, timeout=1)
    except Exception as e:
        print(f"[WARNING] Could not open GPS port: {e}")
        GPS_AVAILABLE = False

# === ENSURE OUTPUT FOLDER EXISTS ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === GPS FIX FUNCTION ===
def get_gps_fix(timeout=10):
    """Attempts to get current GPS coordinates or returns fake coords for testing."""
    if not GPS_AVAILABLE:
        return (40.000000, -86.000000)  # Fake Purdue-like coordinates

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            line = gps_serial.readline().decode('ascii', errors='replace')
            if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                msg = pynmea2.parse(line)
                if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                    return (msg.latitude, msg.longitude)
        except Exception:
            continue
    return (0.0, 0.0)

# === CAMERA INITIALIZATION ===
# NIR = camera 0, RGB = camera 1
print("[INFO] Initializing cameras...")
cam_nir = Picamera2(camera_num=0)
cam_rgb = Picamera2(camera_num=1)

nir_config = cam_nir.create_preview_configuration(
    main={"format": "RGB888", "size": IMAGE_SIZE}
)
rgb_config = cam_rgb.create_preview_configuration(
    main={"format": "RGB888", "size": IMAGE_SIZE}
)

cam_nir.configure(nir_config)
cam_rgb.configure(rgb_config)

cam_nir.start()
cam_rgb.start()

# === NDVI PROCESSING FUNCTION ===
def process_capture():
    # UTC timestamp for filenames
    ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")

    # 1. Get GPS coordinates
    lat, lon = get_gps_fix()

    # 2. Capture both frames
    nir_rgb = cam_nir.capture_array()  # Capture from NIR (camera 0)
    rgb = cam_rgb.capture_array()      # Capture from RGB (camera 1)

    # Convert NIR image to grayscale
    nir = cv2.cvtColor(nir_rgb, cv2.COLOR_BGR2GRAY)

    # 3. Extract red channel from RGB and convert to float
    red = rgb[:, :, 0].astype(np.float32)
    nir_f = nir.astype(np.float32)

    # 4. Compute NDVI = (NIR - Red) / (NIR + Red)
    ndvi = (nir_f - red) / (nir_f + red + 1e-5)

    # 5. Save NDVI GeoTIFF with GPS metadata
    h, w = ndvi.shape
    transform = Affine.translation(lon, lat) * Affine.scale(PIXEL_SIZE, -PIXEL_SIZE)
    out_tif = os.path.join(OUTPUT_DIR, f"{ts}_ndvi.tif")
    with rasterio.open(
        out_tif, "w",
        driver="GTiff",
        height=h, width=w,
        count=1,
        dtype="float32",
        crs=CRS,
        transform=transform
    ) as dst:
        dst.write(ndvi, 1)

    # 6. Create colorized NDVI preview
    ndvi_norm = np.clip((ndvi + 1) / 2, 0, 1)
    ndvi_uint8 = (ndvi_norm * 255).astype(np.uint8)
    preview = cv2.applyColorMap(ndvi_uint8, cv2.COLORMAP_JET)

    out_png = os.path.join(OUTPUT_DIR, f"{ts}_ndvi_color.png")
    cv2.imwrite(out_png, preview)

    print(f"[{ts}] NDVI saved. GPS=({lat:.6f}, {lon:.6f})")

# === CONTINUOUS AUTO-CAPTURE LOOP ===
print(f"NDVI system active. Capturing every {CAPTURE_INTERVAL} seconds...")
print(f"Saving to: {OUTPUT_DIR}")

try:
	time_init = datetime.datetime.now()
	time_cur = time_init
	#time_diff = datetime.datetime.combine(datetime.date.min,time_cur)-datetime.datetime.combine(datetime.date.min,time_init)
	time_diff = time_cur - time_init
	minute_diff = time_diff.seconds*60
	while (minute_diff < MAX_TIME_MIN):
		time_cur = datetime.datetime.now()
		time_diff = time_cur - time_init
		minute_diff = time_diff.seconds/60
		print("minute_diff = "+str(minute_diff))
		process_capture()
		time.sleep(CAPTURE_INTERVAL)

except KeyboardInterrupt:
    print("Capture stopped by user.")

finally:
    cam_nir.stop()
    cam_rgb.stop()
    if GPS_AVAILABLE:
        gps_serial.close()
    print("Cameras and GPS closed. System exiting.")
