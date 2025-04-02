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

# Configure camera
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
    f.write("Timestamp,Filename,ISO,Exposure_Speed\n")

idx = 0
while True:
    now = datetime.now()
    date = now.strftime("%Y%m%d-%H_%M_%S")
    
    # Take photo with auto settings
    filename = f"{date}.jpg"
    photo_path = f"{outdir}/{filename}"
    print(f"[{idx}] Taking photo: {filename}")
    
    camera.capture(photo_path)
    
    # Log the photo settings
    with open(log_file, "a") as f:
        f.write(f"{date},{filename},{camera.iso},{camera.exposure_speed}\n")
    
    print(f"[{idx}] Completed at {date}")
    idx += 1
    
    # Wait for the next interval
    time.sleep(time_interval)

# print("Done.")
