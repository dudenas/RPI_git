from picamera import PiCamera
import time
from datetime import datetime
import os
from PIL import Image, ImageFilter

def detect_blur_pil(image_path, threshold=10):
    """
    Detect if an image is blurry using PIL/Pillow.
    Uses a simple edge detection and measures the mean pixel value.
    Lower values indicate blurrier images.
    
    Returns: (is_blurry, blur_score)
    """
    try:
        # Open the image
        img = Image.open(image_path).convert('L')  # Convert to grayscale
        
        # Apply edge detection filter
        edges = img.filter(ImageFilter.FIND_EDGES)
        
        # Calculate the mean pixel value of the edge-detected image
        pixels = list(edges.getdata())
        blur_score = sum(pixels) / len(pixels)
        
        # Determine if the image is blurry
        is_blurry = blur_score < threshold
        
        return is_blurry, blur_score
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return True, 0  # Assume blurry if there's an error

# Initialize date and directory
now = datetime.now()
day = now.strftime("%Y%m%d")
print(f"date {day}")

# Initialize camera
camera = PiCamera()

# Camera settings
time_interval = 10
max_retries = 3  # Maximum number of retries for blurry photos
blur_threshold = 10  # Adjust this value based on testing

# Initial shutter speed (in microseconds)
# 1/100 second = 10000 microseconds
# Higher values = slower shutter = more light but more blur
# Lower values = faster shutter = less light but less blur
initial_shutter_speed = 10000  # 1/100 second
min_shutter_speed = 1000      # 1/1000 second (very fast)
max_shutter_speed = 100000    # 1/10 second (quite slow)

# Configure camera
camera.resolution = (2592, 1944)
camera.awb_mode = 'auto'
camera.exposure_mode = 'auto'  # Start with auto exposure

# Warm up camera
print("Warming up camera...")
camera.start_preview()
time.sleep(2)

# Create output directories
temp = 0
outdir = f'/home/pi/Desktop/daily_photo/{day}-{temp}'
blurry_dir = None  # Will be set if we need it

# Find an available directory
found = False
while not found:
    isExist = os.path.exists(outdir)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(outdir)
        print(f"Created directory: {outdir}")
        
        # Create a subdirectory for blurry images
        blurry_dir = f"{outdir}/blurry"
        os.makedirs(blurry_dir)
        print(f"Created directory for blurry images: {blurry_dir}")
        
        found = True
    else:
        temp = temp + 1
        outdir = f'/home/pi/Desktop/daily_photo/{day}-{temp}'

# Create a log file
log_file = f"{outdir}/blur_log.txt"
with open(log_file, "w") as f:
    f.write("Timestamp,Filename,Blur_Score,Is_Blurry,Retries,Shutter_Speed\n")

# Main photo capture loop
idx = 0
current_shutter_speed = initial_shutter_speed

while True:
    now = datetime.now()
    date = now.strftime("%Y%m%d-%H_%M_%S")
    
    # Try to take a non-blurry photo
    retries = 0
    got_clear_photo = False
    
    while retries < max_retries and not got_clear_photo:
        # Take a photo
        if retries > 0:
            retry_suffix = f"_retry{retries}"
            
            # If we're retrying, switch to manual exposure and increase shutter speed
            if camera.exposure_mode != 'off':
                print("Switching to manual exposure mode")
                camera.exposure_mode = 'off'
                camera.shutter_speed = current_shutter_speed
                print(f"Setting shutter speed to 1/{current_shutter_speed/1000:.1f} second")
                time.sleep(0.5)  # Let camera adjust
            else:
                # Make shutter speed faster to reduce blur (if we're already in manual mode)
                current_shutter_speed = max(current_shutter_speed // 2, min_shutter_speed)
                camera.shutter_speed = current_shutter_speed
                print(f"Increasing shutter speed to 1/{current_shutter_speed/1000:.1f} second")
                time.sleep(0.5)  # Let camera adjust
        else:
            retry_suffix = ""
            
        filename = f"{date}{retry_suffix}.jpg"
        image_path = f"{outdir}/{filename}"
        
        print(f"Taking photo {idx} (retry {retries})...")
        camera.capture(image_path)
        
        # Check if the photo is blurry
        is_blurry, blur_score = detect_blur_pil(image_path, blur_threshold)
        
        # Log the result
        with open(log_file, "a") as f:
            f.write(f"{date},{filename},{blur_score:.2f},{is_blurry},{retries},{camera.shutter_speed}\n")
        
        if is_blurry:
            print(f"Photo is blurry (score: {blur_score:.2f}). ", end="")
            
            if retries < max_retries - 1:
                print("Retrying...")
                # Move the blurry image to the blurry directory
                os.rename(image_path, f"{blurry_dir}/{filename}")
                retries += 1
            else:
                print("Max retries reached. Keeping the last attempt.")
                got_clear_photo = True  # Give up after max retries
        else:
            print(f"Photo is clear (score: {blur_score:.2f}).")
            got_clear_photo = True
    
    print(f"Photo {idx} saved as {image_path}")
    
    # If we got a clear photo with manual settings, keep those settings
    # Otherwise, reset to auto for the next round
    if not got_clear_photo and camera.exposure_mode == 'off':
        print("Resetting to auto exposure mode")
        camera.exposure_mode = 'auto'
        current_shutter_speed = initial_shutter_speed
    
    # Wait for the next interval
    time.sleep(time_interval)
    idx += 1 