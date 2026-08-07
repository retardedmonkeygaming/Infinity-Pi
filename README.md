InfinityPi 🌌

The Ultimate Disney Infinity Portal Emulator for Raspberry Pi 4B

InfinityPi is a high-performance, Raspberry Pi-based emulator that replicates
the physical Disney Infinity Base. By leveraging the industry-standard emulation
logic from RPCS3 and the hardware foundations of Project DIRE, InfinityPi allows
you to play Disney Infinity 1.0, 2.0, and 3.0 on consoles (PS4, PS3) using
virtual .bin files via a modern web interface or a physical touch sensor.

🚀 Key Features

  - RPCS3 Core Logic: Uses the exact PRNG, Scrambling, and Checksum math from
    the RPCS3 project for 100% authentic console handshake.
  - Modern Web Interface: A mobile-friendly, minimal UI for instant figure
    placement and management.
  - Full Stacking Support: Supports 7 concurrent virtual slots:
      - 2 Character Slots (Player 1 & Player 2)
      - 1 World/Hex Slot (Playsets and Toy Box Expansions)
      - 4 PowerDisc Slots (Stacked underneath players for abilities/costumes).
  - Physical Hardware Support: 1602A LCD display for real-time status and a
    capacitive touch sensor for manual navigation.
  - Real-time Handshake Stream: View raw USB communication between your console
    and the Pi directly in your browser.
  - Pre-loaded Library: Comes configured for Disney Infinity 1.0 and 2.0 figure
    dumps.

🛠️ Hardware Configuration

Controller

  - Raspberry Pi 4B (Required for USB-C OTG/Gadget Mode).
  - Data Link: Connected to the console via the USB-C port.

Display (1602A LCD - 4-bit Mode)

| LCD Pin    | RPi GPIO (BCM) |
| :--------- | :------------- |
| RS         | GPIO 22        |
| Enable (E) | GPIO 17        |
| D4         | GPIO 25        |
| D5         | GPIO 24        |
| D6         | GPIO 23        |
| D7         | GPIO 18        |

Input

  - Capacitive Touch Sensor: GPIO 27.
      - Single Tap: Scroll through current category.
      - Double Tap: Switch categories.
      - Hold (1.2s): Virtually place selected item on Slot 1.

📁 Directory Structure

The script scans for .bin files relatively. Ensure your project folder looks
like this:

InfinityPi/
├── dire_pi.py             # Main Emulator Engine
├── base_identity.sh       # USB Gadget Setup
├── templates/
│   └── index.html         # Web UI
└── bins/
    ├── Characters/        # .bin files for figures
    ├── Playsets/          # .bin files for world pieces
    ├── PowerDiscs/        # .bin files for round/hex discs
    └── Vehicles/          # .bin files for vehicle discs

⚡ Setup Guide

1. Install Dependencies

Ensure your Pi is running the latest OS and has Python 3 installed:

sudo pip3 install flask flask-socketio RPLCD RPi.GPIO

2. Enable USB Gadget Mode

Add the following line to the end of /boot/config.txt:

dtoverlay=dwc2

Add modules-load=dwc2,libcomposite after rootwait in /boot/cmdline.txt.

3. Initialize the USB Identity

Run the provided shell script to mask the Pi as an official Disney Infinity
Base:

sudo bash base_identity.sh

4. Run the Emulator

sudo python3 dire_pi.py

Access the Web UI by navigating to your Pi's IP address (e.g.,
http://192.168.1.15) in any mobile or desktop browser.

📜 Credits

  - RPCS3 Team: Huge thanks to the RPCS3 contributors for the Infinity.cpp
    implementation, which provided the complex PRNG and Scrambling algorithms
    required for console authentication.
  - Project DIRE: Based on the original hardware research and STM32 foundations
    of Project DIRE.
  - Hobbyist Project: Developed as a free-to-use project for the community.
  - AI Assisted: Designed and optimized with the help of AI for low-latency
    performance.

⚖️ License & Contact

  - Developer: vxprxx on Instagram.
  - GitHub: github.com/retardedmonkeygaming
  - Status: Free to use for All.

Disclaimer: This is a hobbyist project and is not affiliated with Disney,
Avalanche Software, or Sony.
