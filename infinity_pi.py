import os, time, sys, threading, json
import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

# --- RPCS3 REPLICATED MATH (STRICTLY UNTOUCHED) ---
def std_rotl(v, count):
    return ((v << count) | (v >> (32 - count))) & 0xFFFFFFFF

class InfinityBase:
    def __init__(self):
        self.random_a = self.random_b = self.random_c = self.random_d = 0
        self.mask = 0x8E55AA1B3999E8AA

    def generate_checksum(self, data, num_bytes):
        return sum(data[:num_bytes]) & 0xFF

    def get_blank_response(self, sequence, res):
        res[0], res[1], res[2] = 0xaa, 0x01, sequence
        res[3] = self.generate_checksum(res, 3)

    def descramble(self, val):
        mask, ret = self.mask, 0
        for i in range(64):
            if mask & 0x8000000000000000:
                ret = (ret << 1) | (val & 0x01)
            val >>= 1
            mask = (mask << 1) & 0xFFFFFFFFFFFFFFFF
        return ret & 0xFFFFFFFF

    def scramble(self, val, garbage):
        mask, ret = self.mask, 0
        for i in range(64):
            ret <<= 1
            if (mask & 1) != 0:
                ret |= (val & 1)
                val >>= 1
            else:
                ret |= (garbage & 1)
                garbage >>= 1
            mask >>= 1
        return ret

    def get_next(self):
        a, b, c, d = self.random_a, self.random_b, self.random_c, self.random_d
        ret = std_rotl(b, 27)
        temp = (a + ((ret ^ 0xFFFFFFFF) + 1)) & 0xFFFFFFFF
        b = (b ^ std_rotl(c, 17)) & 0xFFFFFFFF
        a = d
        c = (c + a) & 0xFFFFFFFF
        ret = (b + temp) & 0xFFFFFFFF
        a = (a + temp) & 0xFFFFFFFF
        self.random_c, self.random_a, self.random_b, self.random_d = a, b, c, ret
        return ret

    def generate_seed(self, seed):
        self.random_a, self.random_b, self.random_c, self.random_d = 0xF1EA5EED, seed, seed, seed
        for _ in range(23): self.get_next()

    def descramble_and_seed(self, buf, sequence, res):
        val = int.from_bytes(buf[4:12], 'big')
        seed = self.descramble(val)
        self.generate_seed(seed)
        self.get_blank_response(sequence, res)

    def get_next_and_scramble(self, sequence, res):
        next_random = self.get_next()
        scrambled = self.scramble(next_random, 0)
        res[0], res[1], res[2] = 0xAA, 0x09, sequence
        res[3:11] = scrambled.to_bytes(8, 'big')
        res[11] = self.generate_checksum(res, 11)

# --- WEB SERVER CONFIG ---
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class InfinityPi_Emulator:
    def __init__(self):
        self.lcd = CharLCD(pin_rs=22, pin_e=17, pins_data=[25, 24, 23, 18], numbering_mode=GPIO.BCM, cols=16, rows=2)
        self.base = InfinityBase()
        
        # Directory Fix: Relative to the script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(script_dir, "bins")
        
        self.categories = ["Characters", "Playsets", "PowerDiscs", "Vehicles"]
        
        self.slots = {}
        for i in range(7):
            sid = 0x20 if i in [0,3,4] else 0x30 if i in [1,5,6] else 0x10
            self.slots[i] = {"name": "Empty", "uid": b"\x00"*7, "data": None, "sid": sid}
        
        self.cat_idx, self.file_idx = 0, 0
        self.files = []
        self.touch_start, self.press_count, self.last_press = 0, 0, 0
        
        print(f"[*] Base Path set to: {self.base_path}")
        for c in self.categories:
            p = os.path.join(self.base_path, c)
            os.makedirs(p, exist_ok=True)
        
        self.load_category()

    def log_to_web(self, tag, data):
        msg = f"[{time.strftime('%H:%M:%S')}] [{tag}] {data.hex()}"
        # Print to terminal
        print(msg)
        # Broadcast to all connected web clients
        socketio.emit('log_update', {'msg': msg}, namespace='/')

    def load_category(self):
        path = os.path.join(self.base_path, self.categories[self.cat_idx])
        self.files = sorted(list(set([f for f in os.listdir(path) if f.lower().endswith('.bin')])))
        self.update_ui()

    def update_ui(self):
        self.lcd.clear()
        self.lcd.write_string(f"CAT:{self.categories[self.cat_idx][:13]}")
        self.lcd.cursor_pos = (1, 0)
        if not self.files: self.lcd.write_string("> Empty")
        else:
            status = "*" if self.slots[0]["data"] else ">"
            self.lcd.write_string(f"{status}{self.files[self.file_idx][:15]}")

    def usb_engine(self):
        fd = os.open("/dev/hidg0", os.O_RDWR)
        while True:
            buf = os.read(fd, 32)
            if not buf or len(buf) < 32: continue

            if buf[0] == 0xff:
                # Immediate echo for handshake log visibility
                self.log_to_web("RECV_AUTH", buf)
                
                command, sequence = buf[2], buf[3]
                q_result = bytearray(32)

                if command == 0x80:
                    q_result[0:24] = [0xaa, 0x15, 0x00, 0x00, 0x0f, 0x01, 0x00, 0x03, 0x02, 0x09, 0x09, 0x43,
                                      0x20, 0x32, 0x62, 0x36, 0x36, 0x4b, 0x34, 0x99, 0x67, 0x31, 0x93, 0x8c]
                elif command == 0x81:
                    self.base.descramble_and_seed(buf, sequence, q_result)
                elif command == 0x83:
                    self.base.get_next_and_scramble(sequence, q_result)
                elif command in [0x90, 0x92, 0x93, 0x95, 0x96, 0xB5]:
                    self.base.get_blank_response(sequence, q_result)
                elif command == 0xA1: # get_present_figures
                    x = 3
                    for i in range(7):
                        if self.slots[i]["data"]:
                            q_result[x], q_result[x+1] = self.slots[i]["sid"] + i, 0x09
                            x += 2
                    q_result[0], q_result[1], q_result[2] = 0xaa, x-2, sequence
                    q_result[x] = self.base.generate_checksum(q_result, x)
                elif command == 0xB4: # get_figure_identifier
                    order = buf[4]
                    q_result[0:4] = [0xaa, 0x09, sequence, 0x00]
                    if order in self.slots and self.slots[order]["data"]:
                        q_result[4:11] = self.slots[order]["uid"]
                    q_result[11] = self.base.generate_checksum(q_result, 11)
                elif command == 0xA2: # query_block
                    order, block = buf[4], buf[5]
                    file_block = 1 if block == 0 else (block * 4)
                    q_result[0:4] = [0xaa, 0x12, sequence, 0x00]
                    if order in self.slots and self.slots[order]["data"] and file_block < 20:
                        q_result[4:20] = self.slots[order]["data"][16*file_block : 16*file_block+16]
                    q_result[20] = self.base.generate_checksum(q_result, 20)

                os.write(fd, q_result)
                self.log_to_web("SENT_AUTH", q_result)

    def handle_touch(self):
        state = GPIO.input(27)
        now = time.time()
        if state:
            if self.touch_start == 0: self.touch_start = now
            if (now - self.touch_start) > 1.2:
                if self.files:
                    p = os.path.join(self.base_path, self.categories[self.cat_idx], self.files[self.file_idx])
                    with open(p, "rb") as f:
                        raw = bytearray(f.read())
                        self.slots[0].update({"name": self.files[self.file_idx], "uid": raw[0:7], "data": raw})
                    self.update_ui()
                    socketio.emit('slot_update', {'slot': 0, 'name': self.files[self.file_idx]})
                while GPIO.input(27): time.sleep(0.01)
                self.touch_start = 0
        else:
            if self.touch_start > 0:
                if (now - self.touch_start) < 0.5: self.press_count += 1; self.last_press = now
                self.touch_start = 0
        if self.press_count > 0 and (now - self.last_press) > 0.3:
            if self.press_count == 1 and self.files:
                self.file_idx = (self.file_idx + 1) % len(self.files)
            elif self.press_count >= 2:
                self.cat_idx = (self.cat_idx + 1) % 4; self.load_category()
            self.update_ui(); self.press_count = 0

emulator = InfinityPi_Emulator()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/files')
def get_files():
    res = {}
    for c in emulator.categories:
        p = os.path.join(emulator.base_path, c)
        if os.path.exists(p):
            res[c] = sorted(list(set([f for f in os.listdir(p) if f.lower().endswith('.bin')])))
        else:
            res[c] = []
    return jsonify(res)

@app.route('/api/place', methods=['POST'])
def web_place():
    d = request.json
    s_idx = int(d['slot'])
    path = os.path.join(emulator.base_path, d['category'], d['filename'])
    with open(path, "rb") as f:
        raw = bytearray(f.read())
        emulator.slots[s_idx].update({"name": d['filename'], "uid": raw[0:7], "data": raw})
    emulator.update_ui()
    return jsonify({"status": "ok"})

@app.route('/api/remove', methods=['POST'])
def web_remove():
    s_idx = int(request.json['slot'])
    emulator.slots[s_idx].update({"name": "Empty", "uid": b"\x00"*7, "data": None})
    emulator.update_ui()
    return jsonify({"status": "ok"})

@app.route('/api/remove_all', methods=['POST'])
def web_remove_all():
    for i in range(7):
        emulator.slots[i].update({"name": "Empty", "uid": b"\x00"*7, "data": None})
    emulator.update_ui()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    threading.Thread(target=emulator.usb_engine, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)