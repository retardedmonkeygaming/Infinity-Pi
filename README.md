```markdown
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

**InfinityPi** is a 1:1 functional replication of the physical **Disney Infinity Base** hardware. Built specifically for the Raspberry Pi 4B, it leverages advanced emulation mathematics from the [RPCS3 Project](https://rpcs3.net/) to satisfy console authentication (PS3/PS4) and features a modern, mobile-friendly **Web Control Portal** for real-time figure management.

---

## 🚀 Key Features

* **RPCS3 Emulation Core:** Strictly replicates the PRNG, scrambling, and checksum logic from `Infinity.cpp`, ensuring 100% accurate handshakes with PS3/PS4 consoles.
* **Enhanced 9-Slot Stacking:** Full support for concurrent virtual items, exceeding standard base limits:
  * 👥 **2x Lead Characters:** Player 1 & Player 2 *(Slots 0 & 1)*
  * 🌍 **3x Hexagonal Stack:** Support for up to 3 stacked Playsets, Toy Box Expansions, or Hex Power Discs in the center *(Slots 2, 7, & 8)*
  * ⚡ **4x PowerDisc Slots:** 2 stacked under Player 1, 2 stacked under Player 2 *(Slots 3–6)*
* **Persistent State Management:** Automatically remembers and re-places all figures across Pi reboots or browser refreshes using `state.json`.
* **Integrated File Explorer:**
  * 🔍 **Instant Search:** Real-time filtering for large figure libraries.
  * 📤 **Web Uploads:** Upload `.bin` figure dumps directly from your phone or PC browser.
* **Live Handshake Stream:** View real-time console communication logs (`RECV_AUTH` / `SENT_AUTH`) directly inside the Web UI.
* **Zero-Config Identity:** Masking script clones the hardware descriptor of an official PDP Disney Infinity Base.

---

## 🛠️ Hardware Requirements

| Component | Function / Details |
| :--- | :--- |
| **Raspberry Pi 4B** | Required for high-speed USB-C OTG / Gadget Mode support. |
| **USB-C Data Cable** | Connects the Pi 4's USB-C port directly to the target console. |
| **Power (Recommended)** | Power via GPIO Pins `2/4` (5V) & Pin `6` (GND) to allow the USB-C port to act purely as a data gadget. |

---

## 📁 Directory Structure

```text
InfinityPi/
├── infinity_pi.py      # Main Emulation Core & Flask Server
├── base_identity.sh    # USB Identity Configuration Script
├── state.json          # Persistent slot storage (auto-generated)
├── templates/
│   └── index.html      # Responsive Search & Control Portal
└── bins/               # Figure Library (.bin dumps)
    ├── 1.0/
    ├── 2.0/
    └── 3.0/
        ├── Characters/
        ├── Playsets/
        └── PowerDiscs/

```

---

## ⚡ Quick Setup

### 1. Install Dependencies

Ensure Python 3 is installed and set up required packages:

```bash
sudo pip3 install flask flask-socketio RPi.GPIO --break-system-packages

```

### 2. Enable USB Gadget Mode

Add the hardware overlay to `/boot/config.txt`:

```ini
dtoverlay=dwc2

```

Append gadget modules to `/boot/cmdline.txt` directly after `rootwait`:

```text
... rootwait modules-load=dwc2,libcomposite ...

```

---

### 3. Initialize USB Identity

Run the configuration script to mask the Pi as an official base:

```bash
sudo bash base_identity.sh

```

---

### 4. Launch the Portal

Start the main emulation engine with root privileges:

```bash
sudo python3 infinity_pi.py

```

> 🌐 **Access the Control Panel:** Open any web browser and navigate to your Pi's IP address:
> `http://<your-pi-ip>`

---

## 📜 Credits & Acknowledgments

* 🎮 **RPCS3 Team:** Core logic, PRNG, and scrambling algorithms.
* 🛠️ **Project DIRE:** Original hardware research and base concepts.
* 🤖 **AI Collaboration:** Technical logic implementation assistance.

---

## ⚖️ License & Contact

| Attribute | Details |
| --- | --- |
| **Developer** | [@vxprxx](https://instagram.com/vxprxx) |
| **GitHub** | [retardedmonkeygaming](https://github.com/retardedmonkeygaming) |
| **Status** | 🟢 Open Source / Hobbyist |

---

> ⚠️ **Disclaimer:** *This project is an independent open-source hobbyist initiative and is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Disney, Avalanche Software, or Sony Interactive Entertainment.*

```

```
