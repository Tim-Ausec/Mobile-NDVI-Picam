set -euo pipefail
OUTDIR="${1:-$HOME/Desktop}"; INTERVAL="${2:-30}"; CAM="${3:-0}"
mkdir -p "$OUTDIR"
while true; do
	ts=$(date +%Y%m%d_%H%M%S_%3N)
	libcamera-still --camera "$CAM" -o "$OUTDIR/capture_${ts}.jpg"
	sleep "$INTERVAL"
done
