import os

HID_PATH = "/dev/hidg0"

try:
    fd = os.open(HID_PATH, os.O_RDWR)
    print("[*] Listening for RAW bytes from PS4. Plug in now...")
    while True:
        data = os.read(fd, 32)
        if data:
            print(f"RECEIVED: {data.hex()}")
except Exception as e:
    print(f"Error: {e}")