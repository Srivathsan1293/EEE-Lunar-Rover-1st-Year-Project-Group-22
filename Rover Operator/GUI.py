"""
Robot Sensor Dashboard — Tkinter GUI + MQTT
============================================
Requirements:
    pip install paho-mqtt

MQTT topics expected (all JSON payloads):
    robot/sensors/ir        → {"value": 74.0, "unit": "cm"}
    robot/sensors/ultrasound→ {"value": 28.0, "unit": "cm"}
    robot/sensors/magnetic  → {"value": 0.42, "unit": "mT"}
    robot/motion            → {"direction": "Forward", "speed": 0.35, "heading": 0}
    robot/geology           → {"rock_type": "Basalt", "age": "3.6 Gya", "classification": "Igneous"}

Broker: localhost:1883 (no auth by default — edit BROKER/PORT below)

Quick test — publish fake data with mosquitto_pub:
    mosquitto_pub -t robot/sensors/ir -m '{"value": 65.0, "unit": "cm"}'
    mosquitto_pub -t robot/motion -m '{"direction": "Forward", "speed": 0.5, "heading": 0}'
"""

import tkinter as tk
from tkinter import ttk, font
import json
import threading
import time
import math
from collections import deque

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("[WARNING] paho-mqtt not installed. Run: pip install paho-mqtt")
    print("[INFO]    Launching in DEMO mode with simulated data.\n")

# ── MQTT config ────────────────────────────────────────────────
BROKER   = "localhost"
PORT     = 1883
TOPICS   = [
    "robot/sensors/ir",
    "robot/sensors/ultrasound",
    "robot/sensors/magnetic",
    "robot/motion",
    "robot/geology",
]

# ── Colour palette ─────────────────────────────────────────────
BG        = "#f7f8fa"
CARD_BG   = "#ffffff"
BORDER    = "#eeeeee"
TEXT_PRI  = "#111111"
TEXT_SEC  = "#999999"
TEXT_MUT  = "#cccccc"
GREEN     = "#4caf50"
ORANGE    = "#ff9800"
BLUE      = "#1a73e8"
RED       = "#e53935"
LIGHT_GRN = "#e8f5e9"
LIGHT_ORG = "#fff8e1"
LIGHT_BLU = "#e3f2fd"
LIGHT_RED = "#ffebee"
SURFACE   = "#f7f8fa"

HISTORY_LEN = 40


# ══════════════════════════════════════════════════════════════
#  Shared state (written by MQTT thread, read by GUI thread)
# ══════════════════════════════════════════════════════════════
class RobotState:
    def __init__(self):
        self.lock = threading.Lock()
        self.ir        = 74.0
        self.us        = 28.0
        self.mag       = 0.42
        self.direction = "Stationary"
        self.speed     = 0.0
        self.heading   = 0
        self.rock_type = "—"
        self.rock_age  = "—"
        self.rock_cls  = "—"
        self.ir_hist   = deque([74.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self.us_hist   = deque([28.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self.mag_hist  = deque([0.42] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self.connected = False
        self.alerts    = deque(maxlen=3)
        self.last_msg  = "Waiting for broker..."

    def update_sensor(self, key, value):
        with self.lock:
            if key == "ir":
                self.ir = value
                self.ir_hist.append(value)
            elif key == "us":
                self.us = value
                self.us_hist.append(value)
                if value < 20:
                    self.alerts.append(f"⚠  Obstacle very close! US = {value:.0f} cm")
            elif key == "mag":
                self.mag = value
                self.mag_hist.append(value)

    def update_motion(self, direction, speed, heading):
        with self.lock:
            self.direction = direction
            self.speed     = speed
            self.heading   = heading

    def update_geology(self, rock_type, age, classification):
        with self.lock:
            self.rock_type = rock_type
            self.rock_age  = age
            self.rock_cls  = classification


state = RobotState()


# ══════════════════════════════════════════════════════════════
#  MQTT client
# ══════════════════════════════════════════════════════════════
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        state.connected = True
        state.last_msg  = f"Connected to {BROKER}:{PORT}"
        for t in TOPICS:
            client.subscribe(t)
    else:
        state.last_msg = f"Connection failed (rc={rc})"

def on_disconnect(client, userdata, rc):
    state.connected = False
    state.last_msg  = "Disconnected from broker"

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        t = msg.topic
        if t == "robot/sensors/ir":
            state.update_sensor("ir", float(payload["value"]))
        elif t == "robot/sensors/ultrasound":
            state.update_sensor("us", float(payload["value"]))
        elif t == "robot/sensors/magnetic":
            state.update_sensor("mag", float(payload["value"]))
        elif t == "robot/motion":
            state.update_motion(
                payload.get("direction", "Unknown"),
                float(payload.get("speed", 0)),
                int(payload.get("heading", 0)),
            )
        elif t == "robot/geology":
            state.update_geology(
                payload.get("rock_type", "—"),
                payload.get("age", "—"),
                payload.get("classification", "—"),
            )
        state.last_msg = f"[{t}] received"
    except Exception as e:
        state.last_msg = f"Parse error: {e}"

def start_mqtt():
    if not MQTT_AVAILABLE:
        return
    client = mqtt.Client()
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.on_message    = on_message
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
    except Exception as e:
        state.last_msg = f"Cannot reach broker: {e}"


# ══════════════════════════════════════════════════════════════
#  Demo mode — simulates data when paho is missing
# ══════════════════════════════════════════════════════════════
import random

DEMO_DIRECTIONS = ["Forward", "Reversing", "Turning Left", "Turning Right", "Stationary"]
DEMO_ROCKS      = [("Basalt","~3.6 Gya","Igneous"),("Granite","~2.1 Gya","Igneous"),
                   ("Sandstone","~450 Mya","Sedimentary"),("Limestone","~300 Mya","Sedimentary")]

def demo_loop():
    ri = 0
    while True:
        state.update_sensor("ir",  max(5,  min(150, state.ir  + random.uniform(-6, 6))))
        state.update_sensor("us",  max(2,  min(100, state.us  + random.uniform(-5, 5))))
        state.update_sensor("mag", max(0,  min(2.0, state.mag + random.uniform(-0.06, 0.06))))
        if random.random() < 0.06:
            state.update_motion(
                random.choice(DEMO_DIRECTIONS),
                round(random.uniform(0, 1.5), 2),
                random.randint(0, 359),
            )
        if random.random() < 0.03:
            r = DEMO_ROCKS[ri % len(DEMO_ROCKS)]
            state.update_geology(*r)
            ri += 1
        state.connected = True
        state.last_msg  = "DEMO MODE — no broker needed"
        time.sleep(0.9)


# ══════════════════════════════════════════════════════════════
#  Sparkline canvas helper
# ══════════════════════════════════════════════════════════════
class Sparkline(tk.Canvas):
    def __init__(self, parent, width=100, height=28, color=GREEN, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=CARD_BG, highlightthickness=0, **kw)
        self._color = color
        self._w = width
        self._h = height

    def update_data(self, data):
        self.delete("all")
        pts = list(data)
        if len(pts) < 2:
            return
        mn, mx = min(pts), max(pts)
        rng = mx - mn or 1
        w, h = self._w, self._h
        coords = []
        for i, v in enumerate(pts):
            x = i / (len(pts) - 1) * w
            y = h - 4 - ((v - mn) / rng) * (h - 8)
            coords += [x, y]
        self.create_line(*coords, fill=self._color, width=1.5,
                         smooth=True, joinstyle=tk.ROUND, capstyle=tk.ROUND)


# ══════════════════════════════════════════════════════════════
#  Compass canvas
# ══════════════════════════════════════════════════════════════
class Compass(tk.Canvas):
    def __init__(self, parent, size=90, **kw):
        super().__init__(parent, width=size, height=size,
                         bg=SURFACE, highlightthickness=0, **kw)
        self._size = size
        self._heading = 0
        self._draw(0)

    def _draw(self, heading):
        s = self._size
        cx = cy = s // 2
        r = s // 2 - 4
        self.delete("all")
        self.create_oval(cx-r, cy-r, cx+r, cy+r,
                         outline=BORDER, fill=SURFACE, width=1)
        # Cardinal labels
        for label, angle in [("N",270),("E",0),("S",90),("W",180)]:
            rad = math.radians(angle)
            lx = cx + (r - 10) * math.cos(rad)
            ly = cy + (r - 10) * math.sin(rad)
            color = RED if label == "N" else TEXT_MUT
            self.create_text(lx, ly, text=label, font=("Courier", 8, "bold"), fill=color)
        # Arrow
        rad = math.radians(heading - 90)
        ax = cx + (r - 18) * math.cos(rad)
        ay = cy + (r - 18) * math.sin(rad)
        self.create_line(cx, cy, ax, ay, fill=BLUE, width=3, arrow=tk.LAST,
                         arrowshape=(10, 12, 4))
        # Centre dot
        self.create_oval(cx-3, cy-3, cx+3, cy+3, fill=TEXT_SEC, outline="")

    def set_heading(self, heading):
        if heading != self._heading:
            self._heading = heading
            self._draw(heading)


# ══════════════════════════════════════════════════════════════
#  Speed arc canvas
# ══════════════════════════════════════════════════════════════
class SpeedArc(tk.Canvas):
    def __init__(self, parent, size=80, **kw):
        super().__init__(parent, width=size, height=size//2+10,
                         bg=CARD_BG, highlightthickness=0, **kw)
        self._size = size
        self._draw(0)

    def _draw(self, speed, max_speed=1.5):
        s = self._size
        self.delete("all")
        cx, cy = s // 2, s // 2
        r = s // 2 - 6
        # Background arc
        self.create_arc(cx-r, cy-r, cx+r, cy+r,
                        start=0, extent=180, style=tk.ARC,
                        outline=BORDER, width=6)
        # Value arc
        pct  = min(speed / max_speed, 1.0)
        ext  = pct * 180
        clr  = GREEN if pct < 0.6 else (ORANGE if pct < 0.85 else RED)
        if ext > 0:
            self.create_arc(cx-r, cy-r, cx+r, cy+r,
                            start=0, extent=ext, style=tk.ARC,
                            outline=clr, width=6)
        self.create_text(cx, cy+4, text=f"{speed:.2f}",
                         font=("Courier", 13, "bold"), fill=TEXT_PRI)
        self.create_text(cx, cy+18, text="m/s",
                         font=("Courier", 8), fill=TEXT_SEC)


# ══════════════════════════════════════════════════════════════
#  D-Pad widget
# ══════════════════════════════════════════════════════════════
class DPad(tk.Frame):
    LAYOUT = [
        (0, 1, "Forward"),
        (1, 0, "Turning Left"),
        (1, 1, "Stationary"),
        (1, 2, "Turning Right"),
        (2, 1, "Reversing"),
    ]
    ICONS = {"Forward":"▲","Reversing":"▼","Turning Left":"◀",
             "Turning Right":"▶","Stationary":"●"}

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=CARD_BG, **kw)
        self._btns = {}
        for row, col, label in self.LAYOUT:
            btn = tk.Label(self, text=self.ICONS[label], width=3, height=1,
                           font=("Arial", 13), bg=SURFACE, fg=TEXT_MUT,
                           relief="flat", bd=0)
            btn.grid(row=row, column=col, padx=3, pady=3, ipadx=4, ipady=3)
            self._btns[label] = btn
        self._active = None

    def set_direction(self, direction):
        if direction == self._active:
            return
        for label, btn in self._btns.items():
            if label == direction:
                btn.config(bg=LIGHT_BLU, fg=BLUE)
            else:
                btn.config(bg=SURFACE, fg=TEXT_MUT)
        self._active = direction


# ══════════════════════════════════════════════════════════════
#  Sensor card frame
# ══════════════════════════════════════════════════════════════
class SensorCard(tk.Frame):
    def __init__(self, parent, title, icon, max_val, bar_color, **kw):
        super().__init__(parent, bg=CARD_BG, bd=1, relief="flat",
                         highlightbackground=BORDER, highlightthickness=1, **kw)
        self._max    = max_val
        self._color  = bar_color
        self._canvas_bar = None

        tk.Label(self, text=icon, font=("Arial", 18), bg=CARD_BG,
                 fg=TEXT_PRI).pack(anchor="w", padx=14, pady=(14,0))
        tk.Label(self, text=title, font=("Courier", 9), bg=CARD_BG,
                 fg=TEXT_SEC).pack(anchor="w", padx=14)

        val_frame = tk.Frame(self, bg=CARD_BG)
        val_frame.pack(anchor="w", padx=14, pady=(2,0))
        self._val_lbl  = tk.Label(val_frame, text="—", font=("Courier", 26, "bold"),
                                   bg=CARD_BG, fg=TEXT_PRI)
        self._val_lbl.pack(side="left", anchor="s")
        self._unit_lbl = tk.Label(val_frame, text="", font=("Courier", 11),
                                   bg=CARD_BG, fg=TEXT_SEC)
        self._unit_lbl.pack(side="left", anchor="s", padx=(3,0))

        # Bar
        bar_bg = tk.Frame(self, bg="#f0f0f0", height=5)
        bar_bg.pack(fill="x", padx=14, pady=(6,0))
        bar_bg.pack_propagate(False)
        self._bar = tk.Frame(bar_bg, bg=bar_color, height=5)
        self._bar.place(x=0, y=0, relheight=1, relwidth=0)

        # Bottom row: badge + sparkline
        bot = tk.Frame(self, bg=CARD_BG)
        bot.pack(fill="x", padx=14, pady=(8,14))
        self._badge = tk.Label(bot, text="—", font=("Courier", 9, "bold"),
                                bg=LIGHT_GRN, fg=GREEN, padx=6, pady=2)
        self._badge.pack(side="left")
        self._spark = Sparkline(bot, width=90, height=26, color=bar_color)
        self._spark.pack(side="right")

    def update(self, value, unit, history):
        disp = f"{value:.0f}" if value >= 10 else f"{value:.2f}"
        self._val_lbl.config(text=disp)
        self._unit_lbl.config(text=unit)
        pct = min(value / self._max, 1.0)
        self._bar.place(relwidth=pct)
        self._spark.update_data(history)

    def set_badge(self, text, bg, fg):
        self._badge.config(text=text, bg=bg, fg=fg)


# ══════════════════════════════════════════════════════════════
#  Main dashboard window
# ══════════════════════════════════════════════════════════════
class Dashboard(tk.Tk):
    REFRESH_MS = 300

    def __init__(self):
        super().__init__()
        self.title("ROVER-7 — Sensor Dashboard")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build_ui()
        self._schedule_refresh()

    # ── layout ────────────────────────────────────────────────
    def _build_ui(self):
        # ── Top bar ──
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(16, 8))

        left_top = tk.Frame(top, bg=BG)
        left_top.pack(side="left")

        title_row = tk.Frame(left_top, bg=BG)
        title_row.pack(anchor="w")
        self._dot = tk.Label(title_row, text="●", font=("Arial", 10),
                              bg=BG, fg=TEXT_MUT)
        self._dot.pack(side="left")
        tk.Label(title_row, text="  ROVER-7", font=("Courier", 16, "bold"),
                 bg=BG, fg=TEXT_PRI).pack(side="left")
        tk.Label(title_row, text="  v2.4.1", font=("Courier", 10),
                 bg=BG, fg=TEXT_SEC).pack(side="left", pady=(4,0))

        self._status_lbl = tk.Label(left_top, text="Connecting…",
                                    font=("Courier", 9), bg=BG, fg=TEXT_SEC)
        self._status_lbl.pack(anchor="w")

        self._clock_lbl = tk.Label(top, text="", font=("Courier", 11),
                                    bg=BG, fg=TEXT_SEC)
        self._clock_lbl.pack(side="right", anchor="n")

        # ── Sensor cards row ──
        sensor_row = tk.Frame(self, bg=BG)
        sensor_row.pack(fill="x", padx=20, pady=(0, 12))
        sensor_row.columnconfigure(0, weight=1)
        sensor_row.columnconfigure(1, weight=1)
        sensor_row.columnconfigure(2, weight=1)

        self._ir_card  = SensorCard(sensor_row, "INFRARED",   "📡", 150, GREEN)
        self._us_card  = SensorCard(sensor_row, "ULTRASOUND", "🔊", 100, ORANGE)
        self._mag_card = SensorCard(sensor_row, "MAGNETIC",   "🧲",   2, BLUE)
        self._ir_card .grid(row=0, column=0, sticky="nsew", padx=(0,6))
        self._us_card .grid(row=0, column=1, sticky="nsew", padx=6)
        self._mag_card.grid(row=0, column=2, sticky="nsew", padx=(6,0))

        # ── Bottom row: motion + geology ──
        bot_row = tk.Frame(self, bg=BG)
        bot_row.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        bot_row.columnconfigure(0, weight=1)
        bot_row.columnconfigure(1, weight=1)

        self._motion_card  = self._build_motion_card(bot_row)
        self._geology_card = self._build_geology_card(bot_row)
        self._motion_card .grid(row=0, column=0, sticky="nsew", padx=(0,6))
        self._geology_card.grid(row=0, column=1, sticky="nsew", padx=(6,0))

        # ── Alert bar (hidden until triggered) ──
        self._alert_var = tk.StringVar(value="")
        self._alert_bar = tk.Label(self, textvariable=self._alert_var,
                                   font=("Courier", 10, "bold"),
                                   bg=LIGHT_RED, fg=RED, pady=6)

    def _card_frame(self, parent):
        f = tk.Frame(parent, bg=CARD_BG, bd=1, relief="flat",
                     highlightbackground=BORDER, highlightthickness=1)
        return f

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Courier", 9), bg=CARD_BG,
                 fg=TEXT_SEC).pack(anchor="w", padx=14, pady=(14, 6))

    def _build_motion_card(self, parent):
        card = self._card_frame(parent)
        self._section_label(card, "MOVEMENT")

        top = tk.Frame(card, bg=CARD_BG)
        top.pack(fill="x", padx=14, pady=(0, 10))

        self._dpad = DPad(top)
        self._dpad.pack(side="left")

        info = tk.Frame(top, bg=CARD_BG)
        info.pack(side="left", padx=16, anchor="n")
        self._dir_lbl = tk.Label(info, text="—", font=("Courier", 18, "bold"),
                                  bg=CARD_BG, fg=TEXT_PRI)
        self._dir_lbl.pack(anchor="w")
        self._hdg_lbl = tk.Label(info, text="—", font=("Courier", 10),
                                  bg=CARD_BG, fg=TEXT_SEC)
        self._hdg_lbl.pack(anchor="w")
        self._path_badge = tk.Label(info, text="Clear path",
                                     font=("Courier", 9, "bold"),
                                     bg=LIGHT_GRN, fg=GREEN, padx=6, pady=2)
        self._path_badge.pack(anchor="w", pady=(6, 0))

        sep = tk.Frame(card, bg=BORDER, height=1)
        sep.pack(fill="x", padx=14)

        bot = tk.Frame(card, bg=CARD_BG)
        bot.pack(fill="x", padx=14, pady=10)

        spd_frame = tk.Frame(bot, bg=CARD_BG)
        spd_frame.pack(side="left")
        tk.Label(spd_frame, text="SPEED", font=("Courier", 8),
                 bg=CARD_BG, fg=TEXT_SEC).pack()
        self._speed_arc = SpeedArc(spd_frame)
        self._speed_arc.pack()

        self._compass = Compass(bot)
        self._compass.pack(side="right", padx=10)

        return card

    def _build_geology_card(self, parent):
        card = self._card_frame(parent)
        self._section_label(card, "GEOLOGICAL DATA")

        fields_row = tk.Frame(card, bg=CARD_BG)
        fields_row.pack(fill="x", padx=14, pady=(0, 10))
        fields_row.columnconfigure(0, weight=1)
        fields_row.columnconfigure(1, weight=1)

        def geo_box(parent, col):
            f = tk.Frame(parent, bg=SURFACE, padx=12, pady=10)
            f.grid(row=0, column=col, sticky="nsew", padx=(0 if col else 0, 6 if col == 0 else 0))
            return f

        rock_box = geo_box(fields_row, 0)
        age_box  = geo_box(fields_row, 1)

        tk.Label(rock_box, text="ROCK TYPE", font=("Courier", 8),
                 bg=SURFACE, fg=TEXT_SEC).pack(anchor="w")
        self._rock_lbl = tk.Label(rock_box, text="—",
                                   font=("Courier", 17, "bold"),
                                   bg=SURFACE, fg=TEXT_PRI)
        self._rock_lbl.pack(anchor="w")
        self._rock_badge = tk.Label(rock_box, text="—",
                                     font=("Courier", 9, "bold"),
                                     bg=LIGHT_BLU, fg=BLUE, padx=6, pady=2)
        self._rock_badge.pack(anchor="w", pady=(6, 0))

        tk.Label(age_box, text="EST. AGE", font=("Courier", 8),
                 bg=SURFACE, fg=TEXT_SEC).pack(anchor="w")
        self._age_lbl = tk.Label(age_box, text="—",
                                  font=("Courier", 17, "bold"),
                                  bg=SURFACE, fg=TEXT_PRI)
        self._age_lbl.pack(anchor="w")
        tk.Label(age_box, text="Confirmed", font=("Courier", 9, "bold"),
                 bg=LIGHT_GRN, fg=GREEN, padx=6, pady=2).pack(anchor="w", pady=(6, 0))

        sep = tk.Frame(card, bg=BORDER, height=1)
        sep.pack(fill="x", padx=14)

        log_frame = tk.Frame(card, bg=CARD_BG)
        log_frame.pack(fill="x", padx=14, pady=10)
        tk.Label(log_frame, text="LAST MESSAGE", font=("Courier", 8),
                 bg=CARD_BG, fg=TEXT_SEC).pack(anchor="w")
        self._msg_lbl = tk.Label(log_frame, text="—", font=("Courier", 9),
                                  bg=CARD_BG, fg=TEXT_SEC, wraplength=260,
                                  justify="left")
        self._msg_lbl.pack(anchor="w", pady=(4, 0))

        return card

    # ── refresh loop ──────────────────────────────────────────
    def _schedule_refresh(self):
        self._refresh()
        self.after(self.REFRESH_MS, self._schedule_refresh)

    def _refresh(self):
        with state.lock:
            ir      = state.ir
            us      = state.us
            mag     = state.mag
            ir_h    = list(state.ir_hist)
            us_h    = list(state.us_hist)
            mag_h   = list(state.mag_hist)
            direct  = state.direction
            speed   = state.speed
            heading = state.heading
            rock    = state.rock_type
            age     = state.rock_age
            cls_    = state.rock_cls
            conn    = state.connected
            alerts  = list(state.alerts)
            lmsg    = state.last_msg

        # Clock
        self._clock_lbl.config(text=time.strftime("%H:%M:%S"))

        # Status dot
        self._dot.config(fg=GREEN if conn else RED)
        self._status_lbl.config(text=lmsg)

        # Sensor cards
        def ir_badge(v):
            if v > 60:  return "Clear",    LIGHT_GRN, GREEN
            if v > 25:  return "Caution",  LIGHT_ORG, ORANGE
            return             "Blocked",  LIGHT_RED, RED

        def us_badge(v):
            if v > 50:  return "Clear",    LIGHT_GRN, GREEN
            if v > 20:  return "Near",     LIGHT_ORG, ORANGE
            return             "Critical", LIGHT_RED, RED

        def mag_badge(v):
            if v > 0.8: return "Strong",   LIGHT_BLU, BLUE
            if v > 0.2: return "Detected", LIGHT_BLU, BLUE
            return             "Weak",     SURFACE,   TEXT_SEC

        self._ir_card .update(ir,  "cm", ir_h)
        self._us_card .update(us,  "cm", us_h)
        self._mag_card.update(mag, "mT", mag_h)
        self._ir_card .set_badge(*ir_badge(ir))
        self._us_card .set_badge(*us_badge(us))
        self._mag_card.set_badge(*mag_badge(mag))

        # Motion
        self._dpad.set_direction(direct)
        self._dir_lbl.config(text=direct)
        self._hdg_lbl.config(text=f"{heading}°  ·  {speed:.2f} m/s")
        self._compass.set_heading(heading)
        self._speed_arc._draw(speed)
        if us < 20:
            self._path_badge.config(text="Obstacle!", bg=LIGHT_RED, fg=RED)
        else:
            self._path_badge.config(text="Clear path", bg=LIGHT_GRN, fg=GREEN)

        # Geology
        self._rock_lbl.config(text=rock)
        self._age_lbl .config(text=age)
        self._rock_badge.config(text=cls_ if cls_ != "—" else "—")
        self._msg_lbl.config(text=lmsg)

        # Alerts
        if alerts:
            self._alert_var.set(alerts[-1])
            self._alert_bar.pack(fill="x", padx=20, pady=(0, 8))
        else:
            self._alert_bar.pack_forget()


# ══════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if MQTT_AVAILABLE:
        t = threading.Thread(target=start_mqtt, daemon=True)
    else:
        t = threading.Thread(target=demo_loop, daemon=True)
    t.start()

    app = Dashboard()
    app.mainloop()