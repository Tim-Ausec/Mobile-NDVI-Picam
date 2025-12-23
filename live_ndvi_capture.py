import time
import datetime
import os
import numpy as np
import cv2
from picamera2 import Picamera2
from rasterio.transform import Affine
import rasterio

# === GPS Optional ===
try:
    import serial, pynmea2
    GPS_AVAILABLE = True
except ImportError:
    print("[INFO] GPS not found — using fake coordinates.")
    GPS_AVAILABLE = False

# === CONFIGURATION ===
OUTPUT_DIR = "/home/pi/ndvi/live_test"
PIXEL_SIZE = 1.0
CRS = "EPSG:4326"
IMAGE_SIZE = (640, 480)
SAVE_INTERVAL = 10  # seconds between saving frames (optional)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === GPS FUNCTION ===
def get_gps_fix(timeout=5):
    if not GPS_AVAILABLE:
        return (40.000000, -86.000000)
    start = time.time()
    while time.time() - start < timeout:
        try:
            line = gps_serial.readline().decode('ascii', errors='replace')
            if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                msg = pynmea2.parse(line)
                return (msg.latitude, msg.longitude)
        except:
            continue
    return (0.0, 0.0)

# === CAMERA SETUP ===
cam_nir = Picamera2(camera_num=0)
cam_rgb = Picamera2(camera_num=1)

nir_config = cam_nir.create_preview_configuration(main={"format": "RGB888", "size": IMAGE_SIZE})
rgb_config = cam_rgb.create_preview_configuration(main={"format": "RGB888", "size": IMAGE_SIZE})

cam_nir.configure(nir_config)
cam_rgb.configure(rgb_config)
cam_nir.start()
cam_rgb.start()

print("[INFO] Live NDVI preview running. Press 'q' to quit.")
last_save = time.time()

try:
    while True:
        # Capture frames
        nir_rgb = cam_nir.capture_array()
        rgb = cam_rgb.capture_array()

        # Convert NIR to grayscale
        nir = cv2.cvtColor(nir_rgb, cv2.COLOR_BGR2GRAY)
        red = rgb[:, :, 0].astype(np.float32)
        nir_f = nir.astype(np.float32)

        # Compute NDVI
        ndvi = (nir_f - red) / (nir_f + red + 1e-5)
        ndvi_norm = np.clip((ndvi + 1) / 2, 0, 1)
        ndvi_uint8 = (ndvi_norm * 255).astype(np.uint8)
        preview = cv2.applyColorMap(ndvi_uint8, cv2.COLORMAP_JET)

        # Show NDVI preview window
        cv2.imshow("NDVI Preview", preview)

        # OPTIONAL: Save every few seconds
        if time.time() - last_save >= SAVE_INTERVAL:
            ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
            out_png = os.path.join(OUTPUT_DIR, f"{ts}_ndvi_color.png")
            cv2.imwrite(out_png, preview)
            print(f"[{ts}] NDVI frame saved.")
            last_save = time.time()

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user.")
finally:
    cam_nir.stop()
    cam_rgb.stop()
    cv2.destroyAllWindows()
    print("Cameras closed. Exiting.")
