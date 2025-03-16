from picamera import PiCamera
import time
from datetime import datetime
import os

now = datetime.now()
day = now.strftime("%Y%m%d")
print(f"date {day}")

camera = PiCamera()

# init camera
time_interval = 60

# Manual settings for the second photo
MANUAL_ISO = 800
MANUAL_SHUTTER_SPEED = 10000  # 1/100 second in microseconds

# make the adjustments
camera.resolution = (2592, 1944)
camera.awb_mode = 'auto'
camera.exposure_mode = 'auto'
camera.start_preview()

print("Warming up camera...")
time.sleep(2)

# create out directory if that does not exit
temp = 0
outdir = f'/home/pi/Desktop/daily_photo/{day}-{temp}'
found = False
while not found:
    isExist = os.path.exists(outdir)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(outdir)
        print(f"Created directory: {outdir}")
        found = True
    else:
        temp = temp + 1
        outdir = f'/home/pi/Desktop/daily_photo/{day}-{temp}'

# Create a log file to track settings
log_file = f"{outdir}/photo_settings.csv"
with open(log_file, "w") as f:
    f.write("Timestamp,Filename,Mode,ISO,Shutter_Speed\n")

idx = 0
while True:
    now = datetime.now()
    date = now.strftime("%Y%m%d-%H_%M_%S")
    
    # Take first photo with auto settings
    auto_filename = f"{date}_auto.jpg"
    auto_path = f"{outdir}/{auto_filename}"
    print(f"[{idx}] Taking auto photo: {auto_filename}")
    
    camera.exposure_mode = 'auto'
    time.sleep(0.5)  # Give camera time to adjust
    camera.capture(auto_path)
    
    # Log the auto photo settings
    with open(log_file, "a") as f:
        f.write(f"{date},{auto_filename},auto,{camera.iso},{camera.exposure_speed}\n")
    
    # Take second photo with manual settings
    manual_filename = f"{date}_manual_iso{MANUAL_ISO}_shutter{MANUAL_SHUTTER_SPEED/1000}.jpg"
    manual_path = f"{outdir}/{manual_filename}"
    print(f"[{idx}] Taking manual photo: {manual_filename}")
    
    # Switch to manual mode
    camera.exposure_mode = 'off'
    camera.iso = MANUAL_ISO
    camera.shutter_speed = MANUAL_SHUTTER_SPEED
    time.sleep(0.5)  # Give camera time to adjust
    
    camera.capture(manual_path)
    
    # Log the manual photo settings
    with open(log_file, "a") as f:
        f.write(f"{date},{manual_filename},manual,{MANUAL_ISO},{MANUAL_SHUTTER_SPEED}\n")
    
    print(f"[{idx}] Completed at {date}")
    idx += 1
    
    # Wait for the next interval
    time.sleep(time_interval)

# print("Done.")
