import os, time, sys, threading, json
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

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
        self.log_mode = "SLOT"
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(script_dir, "bins")
        self.state_file = os.path.join(script_dir, "state.json")
        self.versions = ["1.0", "2.0", "3.0"]
        self.categories = ["Characters", "Playsets", "PowerDiscs", "Vehicles"]
        
        # 9 Slots: 0-1 Leads, 2,7,8 Hex Stack, 3-4 P1 Discs, 5-6 P2 Discs
        self.slots = {}
        for i in range(9):
            # SID Logic: Leads/P1 Discs (0x20), P2/P2 Discs (0x30), Hexes (0x10)
            sid = 0x20 if i in [0,3,4] else 0x30 if i in [1,5,6] else 0x10
            self.slots[i] = {"name": "Empty", "version": "1.0", "category": None, "uid": b"\x00"*7, "data": None, "sid": sid, "path": None}
        
        if not os.path.exists(self.base_path): os.makedirs(self.base_path, exist_ok=True)
        for v in self.versions:
            v_p = os.path.join(self.base_path, v)
            for c in self.categories: os.makedirs(os.path.join(v_p, c), exist_ok=True)
        
        self.load_state()

    def log_to_web(self, tag, data_or_msg, mode="SLOT"):
        if self.log_mode != mode: return
        msg = f"[{time.strftime('%H:%M:%S')}] [{tag}] {data_or_msg.hex() if isinstance(data_or_msg, (bytes, bytearray)) else data_or_msg}"
        socketio.emit('log_update', {'msg': msg}, namespace='/')

    def save_state(self):
        state = {}
        for i, s in self.slots.items():
            if s["data"]:
                state[i] = {"v": s["version"], "c": s["category"], "f": s["name"]}
        with open(self.state_file, "w") as f: json.dump(state, f)

    def load_state(self):
        if not os.path.exists(self.state_file): return
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                for i, info in state.items():
                    idx = int(i)
                    p = os.path.join(self.base_path, info['v'], info['c'], info['f'])
                    if os.path.exists(p):
                        with open(p, "rb") as bf:
                            raw = bytearray(bf.read())
                            self.slots[idx].update({"name": info['f'], "version": info['v'], "category": info['c'], "uid": raw[0:7], "data": raw, "path": p})
        except: pass

    def usb_engine(self):
        fd = os.open("/dev/hidg0", os.O_RDWR)
        while True:
            try:
                buf = os.read(fd, 32)
                if not buf or len(buf) < 32: continue
                if buf[0] == 0xff:
                    with self.lock:
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
                        elif command == 0xA1: 
                            x = 3
                            for i in range(9):
                                if self.slots[i]["data"] is not None:
                                    q_result[x], q_result[x+1] = self.slots[i]["sid"] + i, 0x09
                                    x += 2
                            q_result[0], q_result[1], q_result[2] = 0xaa, x-2, sequence
                            q_result[x] = self.base.generate_checksum(q_result, x)
                        elif command == 0xB4:
                            order = buf[4]
                            q_result[0:4] = [0xaa, 0x09, sequence, 0x00]
                            if order < 9 and self.slots[order]["data"] is not None:
                                q_result[4:11] = self.slots[order]["uid"]
                            q_result[11] = self.base.generate_checksum(q_result, 11)
                        elif command == 0xA2:
                            order, block = buf[4], buf[5]
                            file_block = 1 if block == 0 else (block * 4)
                            q_result[0:4] = [0xaa, 0x12, sequence, 0x00]
                            if order < 9 and self.slots[order]["data"] is not None and file_block < 20:
                                q_result[4:20] = self.slots[order]["data"][16*file_block : 16*file_block+16]
                            q_result[20] = self.base.generate_checksum(q_result, 20)
                        elif command == 0xA3:
                            order, block = buf[4], buf[5]
                            file_block = 1 if block == 0 else (block * 4)
                            q_result[0:4] = [0xaa, 0x02, sequence, 0x00]
                            if order < 9 and self.slots[order]["data"] is not None and file_block < 20:
                                self.slots[order]["data"][16*file_block : 16*file_block+16] = buf[7:23]
                                if self.slots[order]["path"]:
                                    with open(self.slots[order]["path"], "wb") as f: f.write(self.slots[order]["data"])
                            q_result[4] = self.base.generate_checksum(q_result, 4)
                        os.write(fd, q_result)
            except: time.sleep(0.01)

emulator = InfinityPi_Emulator()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({"status": "no file"}), 400
    f = request.files['file']
    ver = request.form.get('version')
    cat = request.form.get('category')
    if f and ver and cat:
        filename = secure_filename(f.filename)
        f.save(os.path.join(emulator.base_path, ver, cat, filename))
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400

@app.route('/api/slots')
def get_slots():
    with emulator.lock: return jsonify({k: v['name'] for k, v in emulator.slots.items()})

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
                emulator.slots[s_idx].update({"name": d['filename'], "version": d['version'], "category": d['category'], "uid": raw[0:7], "data": raw, "path": path})
                emulator.save_state()
        socketio.emit('slot_update', {'slot': s_idx, 'name': d['filename']})
        return jsonify({"status": "ok"})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/remove', methods=['POST'])
def web_remove():
    s_idx = int(request.json['slot'])
    with emulator.lock:
        emulator.slots[s_idx].update({"name": "Empty", "data": None, "path": None})
        emulator.save_state()
    socketio.emit('slot_update', {'slot': s_idx, 'name': "Empty"})
    return jsonify({"status": "ok"})

@app.route('/api/remove_all', methods=['POST'])
def web_remove_all():
    with emulator.lock:
        for i in range(9): emulator.slots[i].update({"name": "Empty", "data": None, "path": None})
        emulator.save_state()
    for i in range(9): socketio.emit('slot_update', {'slot': i, 'name': "Empty"})
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    threading.Thread(target=emulator.usb_engine, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)