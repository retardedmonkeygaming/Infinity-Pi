import os
import time
import sys

HID_PATH = "/dev/hidg0"
PACKET_SIZE = 32

class DisneyBaseEmulator:
    def __init__(self, bin_file_path):
        self.bin_path = bin_file_path
        self.tag_data = None
        self.tag_uid = b""
        self.is_active = False
        self.load_bin()

    def load_bin(self):
        try:
            with open(self.bin_path, "rb") as f:
                self.tag_data = bytearray(f.read())
                self.tag_uid = self.tag_data[0:7]
            print(f"[*] Loaded Character: {self.bin_path} (UID: {self.tag_uid.hex()})")
        except FileNotFoundError:
            print(f"[!] Error: {self.bin_path} not found. Create a 'bins' folder with 'test.bin'.")
            sys.exit(1)

    def calculate_checksum(self, packet):
        return sum(packet[:31]) & 0xFF

    def send_packet(self, dev, response):
        packet = bytearray(response)
        if len(packet) < 31:
            packet.extend([0] * (31 - len(packet)))
        packet.append(self.calculate_checksum(packet))
        dev.write(packet)
        dev.flush() # Force write

    def run(self):
        print(f"[*] Core Engine Started. Monitoring {HID_PATH}...")
        print("[*] Please connect the Pi USB-C port to the PS4 now.")
        
        try:
            # Open with buffering=0 for real-time response
            with open(HID_PATH, "r+b", buffering=0) as dev:
                while True:
                    packet = dev.read(PACKET_SIZE)
                    if len(packet) == 0: continue
                    
                    cmd = packet[0]
                    
                    # 1. Init Handshake
                    if cmd == 0x01:
                        print("<- [PS4] Handshake Request (0x01)")
                        self.send_packet(dev, [0x01, 0x00])
                        print("-> [Pi] Handshake Response Sent")

                    # 2. Slot Control
                    elif cmd == 0x02:
                        state = packet[1]
                        self.is_active = (state == 0x01)
                        self.send_packet(dev, [0x02, state])
                        print(f"<- [PS4] Slot Active: {self.is_active}")

                    # 3. Presence Check
                    elif cmd == 0x03:
                        if self.is_active:
                            # 0x01 = Slot 1, followed by UID
                            res = bytearray([0x03, 0x01]) + self.tag_uid
                            self.send_packet(dev, res)
                        else:
                            self.send_packet(dev, [0x03, 0x00])

                    # 4. Data Read
                    elif cmd == 0x08:
                        block = packet[1]
                        offset = block * 16
                        data = self.tag_data[offset : offset + 16]
                        res = bytearray([0x08, block, 0x01]) + data
                        self.send_packet(dev, res)
                        print(f"<- [PS4] Read Block {block}")

        except KeyboardInterrupt:
            print("\n[*] Stopping...")
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    EMU = DisneyBaseEmulator("bins/test.bin")
    EMU.run()