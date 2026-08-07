# 🌌 InfinityPi

<p align="center">
  <b>The High-Fidelity Disney Infinity Base Emulator for Raspberry Pi 4B</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi%204B-red?style=for-the-badge&logo=raspberrypi" alt="Platform" />
  <img src="https://img.shields.io/badge/Language-Python%203-blue?style=for-the-badge&logo=python" alt="Language" />
  <img src="https://img.shields.io/badge/Framework-Flask%20%7C%20Socket.IO-black?style=for-the-badge&logo=flask" alt="Framework" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Status" />
</p>

---

**InfinityPi** is a 1:1 functional replication of the physical **Disney Infinity Base** hardware. Built specifically for the Raspberry Pi 4B, it leverages the advanced emulation mathematics from the [RPCS3 Project](https://rpcs3.net/) to satisfy console authentication (PS3/PS4) and features a modern, mobile-friendly **Web Control Portal** for real-time figure management.

---

## 🚀 Key Features

* **RPCS3 Emulation Core:** Strictly replicates the PRNG (Pseudo-Random Number Generator), scrambling, and checksum logic from `Infinity.cpp`, ensuring 100% accurate handshakes with PS3/PS4 consoles.
* **Infinity Control Portal:** A sleek, modern Web UI that allows complete portal and base management right from your phone or PC.
* **Full 7-Slot Stacking Support:** Supports up to 7 concurrent virtual items, mirroring physical base behavior:
  * 👥 **2x Lead Characters:** Player 1 & Player 2
  * 🌍 **1x World/Hex Slot:** Playsets or Toy Box Expansions
  * ⚡ **4x PowerDisc Slots:** 2 stacked under Player 1, 2 stacked under Player 2
* **Persistent State Management:** Remembers currently placed figures across browser refreshes and session restarts.
* **Live Handshake Stream:** View real-time console communication logs (`RECV_AUTH` / `SENT_AUTH`) directly inside the Web UI.
* **Pre-loaded Library Support:** Fully optimized out-of-the-box for Disney Infinity 1.0 and 2.0 `.bin` figure dumps.

---

## 🛠️ Hardware Requirements

| Component | Function / Details |
| :--- | :--- |
| **Raspberry Pi 4B** | Required for high-speed USB-C OTG / Gadget Mode support. |
| **USB-C Data Cable** | Connects the Pi 4's USB-C port directly to the target console. |
| **Power (Recommended)** | Power the Pi via GPIO Pins `2/4` (5V) & Pin `6` (GND) to prevent script interruptions during USB bus resets. |

---

## 📁 Directory Structure

The system uses relative pathing to index dumps. Organize your project root as follows:

```text
InfinityPi/
├── dire_pi.py          # Main Emulation Core Engine
├── base_identity.sh    # USB Identity Configuration Script
├── templates/
│   └── index.html      # Responsive Web Control Portal
└── bins/
    ├── Characters/     # Figure dumps (.bin)
    ├── Playsets/       # World & Playset dumps (.bin)
    ├── PowerDiscs/     # Round & Hex disc dumps (.bin)
    └── Vehicles/       # Vehicle & Mount disc dumps (.bin)
```

## ⚡ Quick Setup

### 1. Install Dependencies

Ensure your Pi is running Python 3 and install the core application requirements:

```bash
sudo pip3 install flask flask-socketio RPi.GPIO --break-system-packages

```

### 2. Enable USB Gadget Mode

Add the hardware overlay line to `/boot/config.txt`:

```ini
dtoverlay=dwc2

```

Append `modules-load=dwc2,libcomposite` directly after `rootwait` in `/boot/cmdline.txt`:

```text
... rootwait modules-load=dwc2,libcomposite ...

```

---

### 3. Mask USB Identity

Run the configuration script to mask the Pi's USB descriptor as an official PDP Disney Infinity Base:

```bash
sudo bash base_identity.sh

```

---

### 4. Launch the Portal

Start the main emulation engine with root permissions:

```bash
sudo python3 infinity_pi.py

```

> 🌐 **Access the Control Panel:** Open any browser on your mobile phone or PC and navigate to your Pi's IP address:
> `http://<your-pi-ip>`

---

## 📜 Credits & Acknowledgments

* 🎮 **RPCS3 Team:** Core logic, PRNG, and scrambling algorithms ported directly from the RPCS3 Disney Infinity implementation.
* 🛠️ **Project DIRE:** Originally inspired by the original hardware research and concepts of Project DIRE.
* 🤖 **AI Collaboration:** Designed and optimized with AI assistance for low-latency performance and proper implementation.
**Assistance:** Please contact me on Instagram or open an issue for any assistance.

---

## ⚖️ License & Contact

| Attribute | Details |
| --- | --- |
| **Developer** | [@vxprxx](https://www.google.com/search?q=https://instagram.com/vxprxx) |
| **GitHub Profile** | [retardedmonkeygaming](https://www.google.com/search?q=https://github.com/retardedmonkeygaming) |
| **Status** | Free to use for all |

---

> ⚠️ **Disclaimer:** *This project is an independent open-source hobbyist initiative and is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Disney, Avalanche Software, or Sony Interactive Entertainment.*

```

```
