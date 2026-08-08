import os, time, sys, threading, json
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
        checksum = 0
        for i in range(num_bytes):
            checksum += data[i]
        return checksum & 0xFF

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
        self.random_a = 0xF1EA5EED
        self.random_b = self.random_c = self.random_d = seed
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
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class InfinityPi_Emulator:
    def __init__(self):
        self.lock = threading.Lock()
        self.base = InfinityBase()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(script_dir, "bins")
        self.versions = ["1.0", "2.0", "3.0"]
        self.categories = ["Characters", "Playsets", "PowerDiscs", "ToyBoxes"]
        
        self.slots = {}
        # Hardware SID mapping for 9 positions
        sid_map = {0: 0x20, 1: 0x30, 2: 0x10, 3: 0x11, 4: 0x12, 5: 0x21, 6: 0x22, 7: 0x31, 8: 0x32}
        for i in range(9):
            self.slots[i] = {"name": "Empty", "version": None, "category": None, "uid": b"\x00"*7, "data": None, "sid": sid_map[i]}
        
        if not os.path.exists(self.base_path): os.makedirs(self.base_path, exist_ok=True)
        for v in self.versions:
            v_path = os.path.join(self.base_path, v)
            for c in self.categories:
                os.makedirs(os.path.join(v_path, c), exist_ok=True)

    def log_to_web(self, tag, data_or_msg):
        if isinstance(data_or_msg, (bytes, bytearray)):
            msg = f"[{time.strftime('%H:%M:%S')}] [{tag}] {data_or_msg.hex()}"
        else:
            msg = f"[{time.strftime('%H:%M:%S')}] [{tag}] {data_or_msg}"
        socketio.emit('log_update', {'msg': msg}, namespace='/')

    def persist_to_disk(self, slot_idx):
        slot = self.slots[slot_idx]
        if slot["data"] is None or slot["version"] is None or slot["category"] is None:
            return
        file_path = os.path.join(self.base_path, slot["version"], slot["category"], slot["name"])
        try:
            with open(file_path, "wb") as f:
                f.write(slot["data"])
            self.log_to_web("DISK_WRITE", f"Saved {slot['name']}")
        except Exception as e:
            self.log_to_web("DISK_ERROR", str(e))

    def usb_engine(self):
        fd = os.open("/dev/hidg0", os.O_RDWR)
        while True:
            try:
                buf = os.read(fd, 32)
                if not buf or len(buf) < 32: continue
                # Check for standard command byte at index 0 or index 1 (gadget variance)
                if buf[0] == 0xff or (len(buf) > 1 and buf[1] == 0xff):
                    # Align buffer if offset exists
                    offset = 0 if buf[0] == 0xff else 1
                    with self.lock:
                        command, sequence = buf[offset+2], buf[offset+3]
                        q_result = bytearray(32)

                        if command == 0x80:
                            q_result[0:24] = [0xaa, 0x15, 0x00, 0x00, 0x0f, 0x01, 0x00, 0x03, 0x02, 0x09, 0x09, 0x43,
                                              0x20, 0x32, 0x62, 0x36, 0x36, 0x4b, 0x34, 0x99, 0x67, 0x31, 0x93, 0x8c]
                        elif command == 0x81: self.base.descramble_and_seed(buf[offset:], sequence, q_result)
                        elif command == 0x83: self.base.get_next_and_scramble(sequence, q_result)
                        elif command in [0x90, 0x92, 0x93, 0x95, 0x96, 0xB5]: self.base.get_blank_response(sequence, q_result)
                        elif command == 0xA1: # Presence Check
                            x = 3
                            for i in range(9):
                                if self.slots[i]["data"] is not None:
                                    q_result[x], q_result[x+1] = self.slots[i]["sid"], 0x09
                                    x += 2
                            q_result[0], q_result[1], q_result[2] = 0xaa, x-2, sequence
                            q_result[x] = self.base.generate_checksum(q_result, x)
                        elif command == 0xB4: # UID Check
                            target_sid = buf[offset+4]
                            q_result[0:4] = [0xaa, 0x09, sequence, 0x00]
                            for i in range(9):
                                if self.slots[i]["sid"] == target_sid and self.slots[i]["data"] is not None:
                                    q_result[4:11] = self.slots[i]["uid"]
                                    break
                            q_result[11] = self.base.generate_checksum(q_result, 11)
                        elif command == 0xA2: # Data Read
                            target_sid, block = buf[offset+4], buf[offset+5]
                            file_block = 1 if block == 0 else (block * 4)
                            q_result[0:4] = [0xaa, 0x12, sequence, 0x00]
                            for i in range(9):
                                if self.slots[i]["sid"] == target_sid and self.slots[i]["data"] is not None and file_block < 20:
                                    q_result[4:20] = self.slots[i]["data"][16*file_block : 16*file_block+16]
                                    break
                            q_result[20] = self.base.generate_checksum(q_result, 20)
                        elif command == 0xA3: # Data Write
                            target_sid, block = buf[offset+4], buf[offset+5]
                            file_block = 1 if block == 0 else (block * 4)
                            q_result[0:4] = [0xaa, 0x02, sequence, 0x00]
                            for i in range(9):
                                if self.slots[i]["sid"] == target_sid and self.slots[i]["data"] is not None and file_block < 20:
                                    self.slots[i]["data"][16*file_block : 16*file_block+16] = buf[offset+7:offset+23]
                                    self.persist_to_disk(i)
                                    break
                            q_result[4] = self.base.generate_checksum(q_result, 4)

                        os.write(fd, q_result)
            except Exception: time.sleep(0.01)

emulator = InfinityPi_Emulator()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/slots')
def get_slots():
    with emulator.lock:
        return jsonify({k: v['name'] for k, v in emulator.slots.items()})

@app.route('/api/files')
def get_files():
    res = {}
    for v in emulator.versions:
        res[v] = {}
        for c in emulator.categories:
            p = os.path.join(emulator.base_path, v, c)
            res[v][c] = sorted([f for f in os.listdir(p) if f.lower().endswith('.bin')]) if os.path.exists(p) else []
    return jsonify(res)

@app.route('/api/place', methods=['POST'])
def web_place():
    d = request.json
    s_idx = int(d['slot'])
    path = os.path.join(emulator.base_path, d['version'], d['category'], d['filename'])
    try:
        with open(path, "rb") as f:
            raw = bytearray(f.read())
            with emulator.lock:
                emulator.slots[s_idx].update({"name": d['filename'], "version": d['version'], "category": d['category'], "uid": raw[0:7], "data": raw})
        emulator.log_to_web("SLOT_UPDATE", f"Placed {d['filename']} in Slot {s_idx}")
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/remove', methods=['POST'])
def web_remove():
    s_idx = int(request.json['slot'])
    with emulator.lock:
        emulator.slots[s_idx].update({"name": "Empty", "version": None, "category": None, "uid": b"\x00"*7, "data": None})
    emulator.log_to_web("SLOT_UPDATE", f"Cleared Slot {s_idx}")
    socketio.emit('slot_update', {'slot': s_idx, 'name': "Empty"})
    return jsonify({"status": "ok"})

@app.route('/api/remove_all', methods=['POST'])
def web_remove_all():
    with emulator.lock:
        for i in range(9):
            emulator.slots[i].update({"name": "Empty", "version": None, "category": None, "uid": b"\x00"*7, "data": None})
    for i in range(9):
        socketio.emit('slot_update', {'slot': i, 'name': "Empty"})
    emulator.log_to_web("SLOT_UPDATE", "ALL SLOTS CLEARED")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    threading.Thread(target=emulator.usb_engine, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)