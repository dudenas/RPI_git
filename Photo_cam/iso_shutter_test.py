#!/usr/bin/env python3
from picamera import PiCamera
import time
from datetime import datetime
import os
from PIL import Image

# Create output directory
now = datetime.now()
timestamp = now.strftime("%Y%m%d-%H_%M_%S")
outdir = f'/home/pi/Desktop/camera_test_{timestamp}'

if not os.path.exists(outdir):
    os.makedirs(outdir)
    print(f"Created directory: {outdir}")

# Initialize camera
print("\n=== Initializing Camera ===")
camera = PiCamera()
camera.resolution = (2592, 1944)  # Full resolution
camera.start_preview()

# Warm up camera
print("Warming up camera for 2 seconds...")
time.sleep(2)

# Test combinations of ISO and shutter speed
iso_values = [100, 200, 400, 600, 800]
# Shutter speeds in microseconds: 1/200s, 1/100s, 1/50s, 1/25s
shutter_speeds = [5000, 10000, 20000, 40000]

# Create a report file
report_file = f"{outdir}/camera_test_report.txt"
with open(report_file, "w") as f:
    f.write("ISO,Shutter Speed (1/x sec),Filename,Brightness,File Size (KB)\n")

# Switch to manual mode
camera.exposure_mode = 'off'

# Take photos with different combinations
for iso in iso_values:
    for speed in shutter_speeds:
        print(f"\n=== Testing ISO {iso}, Shutter 1/{speed/1000} sec ===")
        
        # Set camera parameters
        camera.iso = iso
        camera.shutter_speed = speed
        
        # Allow time for the camera to adjust
        time.sleep(1)
        
        # Take photo
        filename = f"iso_{iso}_shutter_1-{int(speed/1000)}.jpg"
        filepath = f"{outdir}/{filename}"
        print(f"Taking photo: {filename}")
        
        camera.capture(filepath)
        
        # Analyze the image
        try:
            with Image.open(filepath) as img:
                # Convert to grayscale and calculate average brightness
                gray_img = img.convert('L')
                pixels = list(gray_img.getdata())
                avg_brightness = sum(pixels) / len(pixels)
                
                file_size = os.path.getsize(filepath) / 1024  # KB
                
                print(f"Average brightness: {avg_brightness:.2f}")
                print(f"File size: {file_size:.2f} KB")
                
                # Write to report
                with open(report_file, "a") as f:
                    f.write(f"{iso},{speed/1000},{filename},{avg_brightness:.2f},{file_size:.2f}\n")
        except Exception as e:
            print(f"Error analyzing image: {e}")

# Clean up
camera.close()
print("\n=== Test Complete ===")
print(f"All test images saved to: {outdir}")
print(f"Report file: {report_file}")

# Display the report
try:
    print("\n=== Camera Test Results ===")
    with open(report_file, "r") as f:
        print(f.read())
except Exception as e:
    print(f"Error displaying report: {e}")

print("\nRecommendations:")
print("- For minimal motion blur: Use faster shutter speeds (1/100 or 1/200)")
print("- For better brightness: Use slower shutter speeds (1/25 or 1/50)")
print("- For NoIR camera: Consider adding infrared lighting for best results")
print("- Optimal balance is usually ISO 400-600 with shutter speed 1/50-1/100") 