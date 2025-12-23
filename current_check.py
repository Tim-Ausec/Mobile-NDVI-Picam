import subprocess
import re
import time

def get_vdd_core_current():
    try:
        # Run the vcgencmd command
        output = subprocess.check_output(['vcgencmd', 'pmic_read_adc'], text=True)

        # Look for the VDD_CORE_A current line
        for line in output.splitlines():
            if "VDD_CORE_A current" in line:
                match = re.search(r"current\(\d+\)=(\d+\.\d+)A", line)
                if match:
                    return float(match.group(1))
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
    return None

# Main loop
try:
    print("Press Ctrl+C to stop...\n")
    while True:
        current = get_vdd_core_current()
        if current is not None:
            print(f"VDD_CORE_A Current: {current:.6f} A")
        else:
            print("Could not read VDD_CORE_A current.")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopped by user.")
