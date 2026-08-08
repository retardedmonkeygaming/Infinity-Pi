# 🌌 InfinityPi

<p align="center">
  <b>The High-Fidelity Disney Infinity Base Emulator for Raspberry Pi</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi%204B-red?style=for-the-badge&logo=raspberrypi" alt="Platform" />
  <img src="https://img.shields.io/badge/Language-Python%203-blue?style=for-the-badge&logo=python" alt="Language" />
  <img src="https://img.shields.io/badge/Framework-Flask%20%7C%20Socket.IO-black?style=for-the-badge&logo=flask" alt="Framework" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Status" />
</p>

---
**InfinityPi** turns a Raspberry Pi into a full-fledged **Disney Infinity Base** emulator. Built to work seamlessly with **PS3, PS4, Wii, and Wii U**, it ports the exact authentication math from the [RPCS3 Infinity Base Emulator](https://rpcs3.net/) to talk to your console directly over USB. You control your entire base instantly from a mobile-friendly web app on your phone or PC.

---

## 📱 Web UI Preview

<p align="center">
  <img src="https://raw.githubusercontent.com/retardedmonkeygaming/Infinity-Pi/94853077e0b1c6ddf8e4a93e08ba8a90bc1ff2e6/Mobile_View.jpeg" width="220" alt="InfinityPi Mobile Interface" style="vertical-align: middle; margin-right: 30px;" />
  <img src="https://raw.githubusercontent.com/retardedmonkeygaming/Infinity-Pi/94853077e0b1c6ddf8e4a93e08ba8a90bc1ff2e6/Desktop_App.png" width="520" alt="InfinityPi Desktop Interface" style="vertical-align: middle;" />
</p>

---

## -> What It Does

* **Cross-Console Support:** Fully compatible with **PS3, PS4, Nintendo Wii, and Wii U** hardware out of the box.
* **RPCS3 Emulation Core:** Uses authentic PRNG, scrambling, and checksum math for instant, reliable console handshakes.
* **Complete Pre-loaded Library:** Comes packed with complete, organized `.bin` figure dumps across **Disney Infinity 1.0, 2.0, and 3.0**. Everything is neatly sorted into folders so you can find characters, playsets, or power discs in seconds (choosable through the WebUI)
* **Mobile-First Web UI:** Built specifically to run smooth on your phone browser while you play. Tap figures on your screen to place or remove them on the fly.
* **Enhanced 9-Slot Stacking:** Exceeds standard base limits with 9 active slots running at once:
  * 👥 **2x Player Slots:** Player 1 & Player 2 *(Slots 0 & 1)*
  * -> **3x Center Slots:** Stack up to 3 Playsets, Toy Box Expansions, or Hex Power Discs simultaneously *(Slots 2, 7, & 8)*
  * ⚡ **4x Ability Slots:** 2 stacked under Player 1; 2 stacked under Player 2 *(Slots 3–6)*
* **In-Built File Manager:** Search large libraries instantly, or upload missing `.bin` dumps straight from your phone (or PC) browser.
* **Auto Save/Restore:** `state.json` tracks your active figures so everything re-places automatically if you reboot the Pi or refresh your browser.

---

<table>
  <tr>
    <td width="50%" valign="top">

### 🔌 Supported Raspberry Pi Models

| RPI | Status |
| :--- | :--- |
| **Raspberry Pi 4B** | Supported |
| **Raspberry Pi 5** | Supported |
| **Raspberry Pi 3A** | Supported |
| **Raspberry Pi Zero** | Supported |
| **Raspberry Pi Zero W/2W** | Supported |
| **Raspberry Pi 3B(+)** | Unsupported |
| **Raspberry Pi 2B** | Unsupported |
| **Raspberry Pi 1B(+)** | Unsupported |

  </td>
    <td width="50%" valign="top">

### 🎮 Supported Consoles

| Console | Status |
| :--- | :--- |
| **PlayStation 4** | Supported |
| **PlayStation 3** | Supported |
| **Nintendo Wii U** | Supported |
| **Nintendo Wii** | Supported |
| **Xbox One / Series X** | Unsupported |
| **Xbox 360** | Unsupported |
| **Nintendo Switch** | Unsupported |

  </td>
  </tr>
</table>
---
## -> Hardware Requirements

| Component | Function / Details |
| :--- | :--- |
| **Raspberry Pi (Check supported model list)** | Required for their OTG (Gadget Mode) controller. |
| **USB Data Cable (Depending on Pi Model)** | Connects the Pi's USB port straight into your console. Use a USB-A Cable for an RPI1A and Micro-USB for all Pi-Zero Models. |
| **External Power (Recommended)** | Power the Pi (those with GPIO) via Pins `2/4` (5V) & Pin `6` (GND) so the USB-C port handles pure data without dropping during console resets. |

---

## 📁 Directory Structure

Everything is pre-organized by game release and item category:

```text
InfinityPi/
├── infinity_pi.py      # Main emulation engine & server
├── base_identity.sh    # USB identity setup script
├── state.json          # Remembers active slots (auto-created)
├── templates/
│   └── index.html      # Mobile Web UI & search panel
└── bins/               # Pre-loaded figure dumps
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

Download the necessary Python libraries on your Pi:

```bash
sudo pip3 install flask flask-socketio RPi.GPIO --break-system-packages

```

### 2. Enable USB Gadget Mode

Add the overlay to `/boot/firmware/config.txt`:

```ini
dtoverlay=dwc2

```

Then append the gadget driver right after `rootwait` in `/boot/firmware/cmdline.txt`:

```text
... rootwait modules-load=dwc2,libcomposite ...

```

---

### 3. Mask USB Identity

Run the shell script to spoof the Pi as an official PDP Disney Infinity Base:

```bash
sudo bash base_identity.sh

```

---

### 4. Run It

Start the emulator with root privileges:

```bash
sudo python3 infinity_pi.py

```

---

### 5. Automated Startup Service (Optional but recommended.)

To have **InfinityPi** start automatically every time your Pi boots up, run the setup script:

```bash
chmod +x create-startup-service.sh
sudo ./create-startup-service.sh

```

> 🌐 **Open the Web UI:** Pull up a browser on your phone or PC and head to:
> `http://<your-pi-ip>`

---

## 📜 Credits & References

* **RPCS3 Team:** Core logic, PRNG, and scrambling algorithms ported from `Infinity.cpp`.
* **Project DIRE:** Original hardware research and concepts.
* **Community:** Developed as an open, free preservation tool for retro gaming.

---

## ⚖️ Contact

| Attribute | Details |
| --- | --- |
| **Developer** | [@vxprxx](https://instagram.com/vxprxx) |
| **GitHub** | [retardedmonkeygaming](https://github.com/retardedmonkeygaming) |
| **Status** | Free & Open Source |

---

> ⚠️ **Disclaimer:** *This is an independent open-source hobbyist project. It is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Disney, Avalanche Software, Sony Interactive Entertainment, or Nintendo.*

> **NOTE:** *In case you use a Pi 3A+, you will have to use a USB Type A to Type A cable.*
```

```
