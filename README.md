# InfinityPi 🌌

InfinityPi is a 1:1 functional software replication of the physical **Disney Infinity Base**. Designed specifically for the Raspberry Pi 4B, it runs the low-level crypto and authentication logic directly on the Pi's USB-C OTG port—allowing you to swap virtual figures in real-time via a mobile web app without needing physical toys or bases.

It natively supports **Wii, Wii U, PS3, and PS4** consoles using standard `.bin` dumps.

---

## 💡 How It Works

Physical Disney Infinity bases rely on specific PRNG, packet scrambling, and checksum math during initial console handshakes. InfinityPi uses the reverse-engineered `Infinity.cpp` implementation from the [RPCS3 Project](https://rpcs3.net/) combined with Linux's `ConfigFS` USB gadget framework.

By emulating the exact vendor descriptors of a PDP Disney Infinity base, the target console accepts the Pi 4B as real hardware. A lightweight Flask backend then manages virtual placement across all 9 internal base slots.

---

## ⚡ Key Capabilities

* **Authentic USB Handshaking:** Replicates the exact scrambling algorithms for 100% reliable console pairing on Wii, Wii U, PS3, and PS4.
* **Expanded 9-Slot Virtual Stacking:**
  * **Slots 0 & 1:** Player 1 & Player 2 Characters
  * **Slots 2, 7, & 8:** Center Hexagonal Stack (Up to 3 concurrent Playsets, Expansions, or Hex Discs)
  * **Slots 3–6:** Player PowerDiscs (2 stacked per player slot)
* **Instant Web UI:** Accessible from any phone, tablet, or desktop browser on your local network. Features instant search filtering and live file uploading for new `.bin` dumps.
* **Persistent Base State:** Automatically saves active slots to disk (`state.json`). Powering off the Pi or refreshing your browser won't clear your active figures.
* **Live Auth Stream:** Debug raw USB packet exchanges (`RECV_AUTH` / `SENT_AUTH`) live in the web control panel.

---

## 🛠️ Hardware Requirements

| Component | Purpose |
| :--- | :--- |
| **Raspberry Pi 4B** | Required for high-speed USB-C OTG / Gadget mode capabilities. |
| **USB-C Data Cable** | Plugs directly from the Pi 4's USB-C port into your console. |
| **Power (5V GPIO)** | **Recommended:** Power the Pi via GPIO Pin 2/4 (5V) & Pin 6 (GND). This keeps the USB-C port acting purely as a data line and prevents power-cycle drops during console USB resets. |

---

## 📁 Directory Layout

Organize your `.bin` library inside the `bins/` directory. Path resolution is relative to the core script:

```text
InfinityPi/
├── infinity_pi.py      # Core Emulation Logic & Flask App
├── base_identity.sh    # ConfigFS USB Gadget Setup Script
├── state.json          # Active base slot storage (Auto-generated)
├── templates/
│   └── index.html      # Responsive Web Control Panel
└── bins/               # Dump storage directory
    ├── 1.0/
    ├── 2.0/
    └── 3.0/
        ├── Characters/
        ├── Playsets/
        └── PowerDiscs/

```

---

## 🚀 Installation & Running

### 1. Install System Dependencies

Ensure you are running a 64-bit Pi OS installation with Python 3:

```bash
sudo pip3 install flask flask-socketio RPi.GPIO --break-system-packages

```

### 2. Configure USB Gadget Mode

Enable the `dwc2` overlay in `/boot/config.txt`:

```ini
dtoverlay=dwc2

```

Enable composite driver loading in `/boot/cmdline.txt` (add it immediately after `rootwait` on the same line):

```text
modules-load=dwc2,libcomposite

```

### 3. Initialize Base Identity

Execute the gadget initialization script to mask the Pi as an official USB peripheral:

```bash
sudo bash base_identity.sh

```

### 4. Start the Server

Run the main process with root permissions (required for direct USB gadget interaction):

```bash
sudo python3 infinity_pi.py

```

Open your browser and navigate to `http://<your-pi-ip>` or `http://raspberrypi.local:5000` to access the portal.

---

## 📜 Credits

* **RPCS3 Team:** Core reverse-engineering of the Disney Infinity base hardware interface (`Infinity.cpp`).
* **Project DIRE:** Original hardware concepts and research on base emulation.

---

## ⚖️ License & Disclaimer

Developed by [@vxprxx](https://instagram.com/vxprxx) | Repo: [retardedmonkeygaming](https://github.com/retardedmonkeygaming)

*This project is an independent open-source research effort and is not affiliated, endorsed, or associated with Disney, Avalanche Software, Nintendo, or Sony Interactive Entertainment. All product names, logos, and brands are property of their respective owners.*

```

```