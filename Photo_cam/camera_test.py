#!/usr/bin/env python3
from picamera import PiCamera
import time
from datetime import datetime
import os
from PIL import Image
import subprocess

def print_section(title):
    """Print a section title with separators for better readability"""
    print("\n" + "="*50)
    print(f" {title} ".center(50, "-"))
    print("="*50)

# Initialize camera
print_section("INITIALIZING CAMERA")
camera = PiCamera()
print("Camera initialized successfully!")

# Display camera info
print_section("CAMERA INFORMATION")
print(f"Camera revision: {camera.revision}")
print(f"Default resolution: {camera.resolution}")
print(f"Default framerate: {camera.framerate}")
print(f"Sensor mode: {camera.sensor_mode}")

# Show available settings
print_section("AVAILABLE SETTINGS")
print("Available AWB (Auto White Balance) modes:")
for mode in camera.AWB_MODES:
    print(f"  - {mode}")

print("\nAvailable exposure modes:")
for mode in camera.EXPOSURE_MODES:
    print(f"  - {mode}")

print("\nAvailable image effects:")
for effect in camera.IMAGE_EFFECTS:
    print(f"  - {effect}")

# Create output directory for test images
print_section("CREATING OUTPUT DIRECTORY")
now = datetime.now()
timestamp = now.strftime("%Y%m%d-%H_%M_%S")
outdir = f'/home/pi/Desktop/camera_test_{timestamp}'

if not os.path.exists(outdir):
    os.makedirs(outdir)
    print(f"Created directory: {outdir}")

# Camera warm-up
print_section("WARMING UP CAMERA")
print("Warming up camera for 2 seconds...")
camera.start_preview()
time.sleep(2)

# Take a test picture with default settings
print_section("TAKING TEST PICTURE WITH DEFAULT SETTINGS")
camera.resolution = (2592, 1944)  # Max resolution
camera.awb_mode = 'auto'
camera.exposure_mode = 'auto'

test_image_path = f"{outdir}/test_default.jpg"
camera.capture(test_image_path)
print(f"Captured test image: {test_image_path}")

# Display image information
print_section("IMAGE INFORMATION")
try:
    with Image.open(test_image_path) as img:
        width, height = img.size
        format = img.format
        mode = img.mode
        
        print(f"Resolution: {width} x {height}")
        print(f"Format: {format}")
        print(f"Mode: {mode}")
        print(f"File size: {os.path.getsize(test_image_path) / 1024:.2f} KB")
except Exception as e:
    print(f"Error reading image information: {e}")

# Test different AWB modes
print_section("TESTING DIFFERENT AWB MODES")
test_modes = ['auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon']
for mode in test_modes:
    if mode in camera.AWB_MODES:
        print(f"Testing AWB mode: {mode}")
        camera.awb_mode = mode
        time.sleep(1)  # Give camera time to adjust
        mode_image_path = f"{outdir}/test_awb_{mode}.jpg"
        camera.capture(mode_image_path)
        print(f"  Captured image with {mode} AWB mode: {mode_image_path}")

# Test different exposure modes
print_section("TESTING DIFFERENT EXPOSURE MODES")
test_exp_modes = ['auto', 'night', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks']
for mode in test_exp_modes:
    if mode in camera.EXPOSURE_MODES:
        print(f"Testing exposure mode: {mode}")
        camera.exposure_mode = mode
        time.sleep(1)  # Give camera time to adjust
        mode_image_path = f"{outdir}/test_exp_{mode}.jpg"
        camera.capture(mode_image_path)
        print(f"  Captured image with {mode} exposure mode: {mode_image_path}")

# Reset to auto settings
camera.awb_mode = 'auto'
camera.exposure_mode = 'auto'

# Take a final picture with auto settings
print_section("TAKING FINAL PICTURE WITH AUTO SETTINGS")
final_image_path = f"{outdir}/final_auto.jpg"
camera.capture(final_image_path)
print(f"Captured final image with auto settings: {final_image_path}")

# Clean up
print_section("CLEANING UP")
camera.close()
print("Camera closed.")

# Display summary
print_section("SUMMARY")
print(f"All test images saved to: {outdir}")
print(f"Total images captured: {len(os.listdir(outdir))}")
print("\nTest completed successfully!")

# Try to display the default image if running in desktop environment
try:
    subprocess.run(["xdg-open", test_image_path], check=False)
    print(f"\nOpening default test image: {test_image_path}")
except Exception:
    print("\nCannot open image automatically. Please check the saved images manually.") 