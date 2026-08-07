This is the updated README.md specifically tailored to the current state of
InfinityPi, removing the 1602A display requirements and focusing on the new Web
Portal and RPCS3-based logic.

InfinityPi 🌌

The High-Fidelity Disney Infinity Base Emulator for Raspberry Pi 4B

InfinityPi is a 1:1 functional replication of the Disney Infinity Base hardware.
Built for the Raspberry Pi 4B, it utilizes the advanced emulation mathematics
from the RPCS3 Project to satisfy console authentication (PS4/PS3) and features
a modern, mobile-friendly Web Portal for real-time figure management.

🚀 Key Features

  - RPCS3 Emulation Core: Strictly replicates the PRNG (Pseudo-Random Number
    Generator), Scrambling, and Checksum logic from Infinity.cpp, ensuring
    perfect handshakes with PS4/PS3 consoles.
  - Infinity Control Portal: A sleek Web UI that allows you to manage the portal
    from your phone or PC.
  - Full Stacking Logic: Supports up to 7 concurrent virtual items, stacking
    exactly like the physical base:
      - 2 Lead Characters (Player 1 & Player 2)
      - 1 World/Hex Slot (Playsets or Toy Box Expansions)
      - 4 PowerDisc Stacks (2 for Player 1, 2 for Player 2).
  - Persistent State: The portal remembers what figures are placed even if you
    refresh the browser page.
  - Live Handshake Stream: A real-time console log in the Web UI showing raw USB
    communication (RECV_AUTH / SENT_AUTH).
  - Pre-loaded Library: Optimized for Disney Infinity 1.0 and 2.0 .bin dumps.

🛠️ Hardware Requirements

  - Raspberry Pi 4B: Required for its high-speed USB-C OTG (Gadget Mode)
    capabilities.
  - USB-C Data Cable: Connects the Pi 4's USB-C port to the Console.
  - Power (Recommended): Power the Pi via GPIO Pins 2/4 (5V) and 6 (GND) to
    prevent the script from dying during USB resets.

📁 Directory Structure

The system uses relative pathing. Place your .bin files inside the bins folder
located within the project directory:

InfinityPi/
├── dire_pi.py             # Main Emulation Engine
├── base_identity.sh       # USB Identity Configuration
├── templates/
│   └── index.html         # Web Control Portal
└── bins/
    ├── Characters/        # Figure dumps
    ├── Playsets/          # World piece dumps
    ├── PowerDiscs/        # Round/Hex disc dumps
    └── Vehicles/          # Vehicle disc dumps

⚡ Quick Setup

1. Install Dependencies

sudo pip3 install flask flask-socketio RPi.GPIO

2. Enable USB Gadget Mode

Edit /boot/config.txt and add:

dtoverlay=dwc2

Edit /boot/cmdline.txt and add this after rootwait:

modules-load=dwc2,libcomposite

3. Mask USB Identity

Run the setup script to identify the Pi as a PDP Disney Infinity Base:

sudo bash base_identity.sh

4. Launch the Portal

sudo python3 dire_pi.py

Access the control panel by visiting http://<your-pi-ip> in your phone's
browser.

📜 Credits

  - RPCS3 Team: Core logic, PRNG, and Scrambling algorithms ported from the
    RPCS3 Disney Infinity implementation.
  - Project DIRE: Originally inspired by the hardware research of Project DIRE.
  - Developer: Developed and maintained by vxprxx (Instagram).
  - GitHub: retardedmonkeygaming

⚖️ License

  - Status: Free to use for all hobbyists.
  - Disclaimer: This is an independent hobbyist project and is not affiliated
    with Disney, Avalanche Software, or Sony. Developed with the assistance of
    AI.
