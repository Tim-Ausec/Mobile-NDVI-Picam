# PiCamera-Module
Codebase for raspberry pi 5-based image capture and analysis module

# CamBox Operation Summary (10-09-2025)

## Files used for CamBox operation:

- agrovolo.sh
- CamBox.py
- cron_stop.sh

## cron tasks
Run 'crontab -e' in terminal to see cron tasks

```
@reboot agrovolo.sh
```

Cron is a scheduler used to execute tasks at specific times. @reboot tells cron to run the following command on startup.

As can be seen, agrovolo.sh is run on startup.

## agrovolo.sh

```
#! /bin/bash
sudo python /home/agrovolo/Desktop/Agrovolo-Imager-main/CamBox.py
sudo systemctl poweroff
```

This bash script first runs CamBox.py and then shuts the pi down.

## CamBox.py
This script takes pictures at evenly spaced intervals of time and stores them. After a predefined period of time, the script stops taking pictures and finishes.

## cron_stop.sh

```
#! /bin/bash
pkill -f agrovolo.sh
pkill -f python
```

This script is manually run with './cron_stop.sh' in the terminal to kill the agrovolo.sh script and the python script. This ensures that the pi does not shut down automatically so that developers can have adequate time to implement changes and debug.

