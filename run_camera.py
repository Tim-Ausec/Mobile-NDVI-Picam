import os
import sys
import time
import subprocess
import re
from datetime import datetime
from picamera2 import Picamera2

def get_vdd_core_current():
    try:
        output = subprocess.check_output(['vcgencmd', 'pmic_read_adc'], text=True)
        for line in output.splitlines():
            if "VDD_CORE_A current" in line:
                match = re.search(r"current\(\d+\)=(\d+\.\d+)A", line)
                if match:
                    return float(match.group(1))
    except subprocess.CalledProcessError:
        return None
    return None

def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop")
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    cam = sys.argv[3] if len(sys.argv) > 3 else "0"

    os.makedirs(outdir, exist_ok=True)
    logfile = os.path.join(outdir, "camera_current_log.txt")
    
    

    print(f"Logging current measurements to: {logfile}")
    print("Press Ctrl+C to stop.\n")

    try:
        with open(logfile, "a") as log:
            while True:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Measure before picture
                current_off = get_vdd_core_current()
                if current_off is not None:
                    log.write(f"[{ts}] CAMERA OFF: {current_off:.3f} amps\n")

                # Take picture
                filename = os.path.join(outdir, f"capture_{ts.replace(' ', '_').replace(':','')}.jpg")
                subprocess.run(["libcamera-still", "--camera", cam, "-o", filename], check=True)

                # Measure after picture
                current_on = get_vdd_core_current()
                if current_on is not None:
                    log.write(f"[{ts}] CAMERA ON: {current_on:.3f} amps\n")

                log.flush()
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()


