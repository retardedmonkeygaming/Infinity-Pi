# 🌌 InfinityPi

<p align="center">
  <b>The Ultimate Disney Infinity Portal Emulator for Raspberry Pi 4B</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi%204B-red?style=for-the-badge&logo=raspberrypi" alt="Platform" />
  <img src="https://img.shields.io/badge/Language-Python%203-blue?style=for-the-badge&logo=python" alt="Language" />
  <img src="https://img.shields.io/badge/Framework-Flask%20%7C%20Socket.IO-black?style=for-the-badge&logo=flask" alt="Framework" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Status" />
</p>

---

**InfinityPi** is a high-performance Raspberry Pi-based emulator that replicates the physical **Disney Infinity Base**. Powered by the authentic emulation logic from [RPCS3](https://rpcs3.net/) and built on the hardware foundations of **Project DIRE**, InfinityPi lets you play *Disney Infinity 1.0, 2.0, and 3.0* on modern and legacy consoles (PS3, PS4) using virtual `.bin` files controlled via a web interface or physical touch sensor.

---

## 🚀 Key Features

* **Authentic RPCS3 Core Logic:** Utilizes the exact PRNG, scrambling, and checksum math from RPCS3 for a 100% genuine console authentication handshake.
* **Modern Web Interface:** A lightweight, mobile-responsive UI designed for instant figure placement and base management.
* **Full 7-Slot Stacking Support:**
  * 👥 **2x Character Slots:** Player 1 & Player 2
  * 🌍 **1x World/Hex Slot:** Playsets & Toy Box Expansions
  * ⚡ **4x PowerDisc Slots:** Ability & costume discs stacked under active players
* **Hardware Interfacing:** Real-time display updates via a 1602A LCD and manual navigation using a capacitive touch sensor.
* **USB Handshake Stream:** Inspect raw USB packet communications between the Pi and the console directly from your browser.
* **Pre-loaded Library Support:** Fully prepared out-of-the-box for Disney Infinity 1.0 and 2.0 figure dumps.

---

## 🛠️ Hardware Configuration

### 🔌 Main Controller
* **Device:** Raspberry Pi 4B *(Required for USB-C OTG / Gadget Mode)*
* **Data Connection:** Connect the Pi's **USB-C port** directly to the console.

### 📺 Display (1602A LCD - 4-bit Mode)

| LCD Pin | Function | RPi GPIO (BCM) |
| :--- | :--- | :--- |
| **RS** | Register Select | `GPIO 22` |
| **E** | Enable | `GPIO 17` |
| **D4** | Data Bit 4 | `GPIO 25` |
| **D5** | Data Bit 5 | `GPIO 24` |
| **D6** | Data Bit 6 | `GPIO 23` |
| **D7** | Data Bit 7 | `GPIO 18` |

### 👆 Physical Control
* **Capacitive Touch Sensor:** `GPIO 27`
  * 🔹 **Single Tap:** Scroll forward through items in current category
  * 🔹 **Double Tap:** Cycle through categories (*Characters, Playsets, Discs, Vehicles*)
  * 🔹 **Hold (1.2s):** Place selected item onto **Slot 1**

---

## 📁 Directory Structure

The emulator scans for file paths relative to the project root. Structure your workspace as follows:

```text
InfinityPi/
├── dire_pi.py          # Main Emulator Core Engine
├── base_identity.sh    # USB Gadget Configuration Script
├── templates/
│   └── index.html      # Responsive Web UI
└── bins/
    ├── Characters/     # Figure dumps (.bin)
    ├── Playsets/       # World & Playset dumps (.bin)
    ├── PowerDiscs/     # Ability & Costume discs (.bin)
    └── Vehicles/       # Vehicle & Mount discs (.bin)

```markdown
## ⚡ Quick Setup Guide

### 1. Install Dependencies
Ensure your Pi is updated and running Python 3 before installing required modules:

```bash
sudo pip3 install flask flask-socketio RPLCD RPi.GPIO

```

### 2. Enable USB Gadget Mode

Add the hardware overlay definition to `/boot/config.txt`:

```ini
dtoverlay=dwc2

```

Then append `modules-load=dwc2,libcomposite` directly after `rootwait` in `/boot/cmdline.txt`:

```text
... rootwait modules-load=dwc2,libcomposite ...

```

---

### 3. Initialize USB Identity

Run the provided setup script to spoof the Pi's USB descriptor as an official physical **Disney Infinity Base**:

```bash
sudo bash base_identity.sh

```

---

### 4. Launch the Emulator

Execute the main engine with root privileges:

```bash
sudo python3 dire_pi.py

```

> 🌐 **Access the Control Panel:** Open any desktop or mobile browser and navigate to your Pi's local network address:
> `http://192.168.1.15` *(replace with your Pi's actual IP)*

---

## 📜 Credits & Acknowledgments

* 🎮 **RPCS3 Team:** Special thanks to the RPCS3 contributors for the `Infinity.cpp` reference implementation detailing the complex PRNG and scrambling algorithms.
* 🛠️ **Project DIRE:** Built upon original hardware research and STM32 architecture concepts from Project DIRE.
* 🕹️ **Community:** Developed as an open, free-to-use hobbyist project dedicated to video game preservation.

---

## ⚖️ License & Contact

| Attribute | Details |
| --- | --- |
| **Developer** | [@vxprxx](https://www.google.com/search?q=https://instagram.com/vxprxx) |
| **GitHub Profile** | [retardedmonkeygaming](https://www.google.com/search?q=https://github.com/retardedmonkeygaming) |
| **Status** | 🟢 Free & Open Source for Everyone |

---

> ⚠️ **Disclaimer:** *This project is an independent, non-commercial open-source initiative and is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Disney, Avalanche Software, or Sony Interactive Entertainment.*

```

```
