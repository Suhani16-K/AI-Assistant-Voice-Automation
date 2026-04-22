"""
gui/hud.py
NEXUS — Advanced Intelligence Interface
Green circular HUD with hexagon patterns and orbital rings
"""

import math
import threading
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPointF, QRectF, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont,
    QLinearGradient, QRadialGradient, QPainterPath,
    QFontDatabase, QPalette
)


# ══════════════════════════════════════════════
#  WORKER THREADS
# ══════════════════════════════════════════════
class ProcessWorker(QThread):
    done      = pyqtSignal(str)
    skill_out = pyqtSignal(str)
    status    = pyqtSignal(str)

    def __init__(self, brain, dispatcher, text):
        super().__init__()
        self.brain = brain
        self.dispatcher = dispatcher
        self.text = text

    def run(self):
        self.status.emit("PROCESSING")
        result, name = self.dispatcher.dispatch(self.text)
        if result:
            self.skill_out.emit(result)
        reply = self.brain.process(self.text)
        self.done.emit(reply)
        self.status.emit("STANDBY")


class ListenWorker(QThread):
    heard  = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, voice):
        super().__init__()
        self.voice = voice
        self._on = True

    def run(self):
        while self._on:
            self.status.emit("LISTENING")
            text = self.voice.listen(timeout=5, phrase_limit=10)
            if text:
                self.heard.emit(text)
            self.status.emit("STANDBY")

    def stop(self):
        self._on = False


# ══════════════════════════════════════════════
#  CENTRAL ORB  — green circular reactor
# ══════════════════════════════════════════════
class CentralOrb(QWidget):
    clicked = pyqtSignal()

    STATUS_COLORS = {
        "STANDBY":    (QColor(0, 220, 120),   QColor(0, 180, 90)),
        "LISTENING":  (QColor(50, 255, 180),  QColor(0, 220, 140)),
        "PROCESSING": (QColor(255, 200, 0),   QColor(200, 150, 0)),
        "SPEAKING":   (QColor(0, 240, 200),   QColor(0, 190, 160)),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self._angle  = 0.0
        self._angle2 = 0.0
        self._pulse  = 0.0
        self._pdir   = 1
        self._status = "STANDBY"
        self._wave   = [0.0] * 32
        self._wave_t = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        t = QTimer(self); t.timeout.connect(self._tick); t.start(25)

    def _tick(self):
        self._angle   = (self._angle  + 1.2) % 360
        self._angle2  = (self._angle2 - 0.7) % 360
        self._pulse  += 0.05 * self._pdir
        if self._pulse >= 1.0: self._pdir = -1
        elif self._pulse <= 0.0: self._pdir = 1
        self._wave_t += 0.12
        for i in range(len(self._wave)):
            self._wave[i] = math.sin(self._wave_t + i * 0.4) * 0.5 + 0.5
        self.update()

    def set_status(self, s: str):
        self._status = s; self.update()

    def mousePressEvent(self, e):
        self.clicked.emit()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width()/2, self.height()/2
        R = min(cx, cy) - 8
        col, col2 = self.STATUS_COLORS.get(self._status, self.STATUS_COLORS["STANDBY"])

        # ── outermost glow halos ──
        for i in range(4, 0, -1):
            alpha = int(15 + 10 * self._pulse) * i // 4
            p.setPen(QPen(QColor(col.red(), col.green(), col.blue(), alpha), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), R + i*7, R + i*7)

        # ── outer dashed orbit ring ──
        pen = QPen(QColor(col.red(), col.green(), col.blue(), 60), 1, Qt.PenStyle.DashLine)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), R, R)

        # ── 3 rotating arc segments ──
        for seg in range(3):
            base_angle = self._angle + seg * 120
            pen2 = QPen(col, 2.5)
            pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen2); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(cx-R, cy-R, R*2, R*2),
                      int(base_angle*16), int(55*16))

        # ── inner counter-rotating ring ──
        r2 = R * 0.78
        for seg in range(6):
            base2 = self._angle2 + seg * 60
            pen3 = QPen(QColor(col2.red(), col2.green(), col2.blue(), 150), 1.5)
            pen3.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen3); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(cx-r2, cy-r2, r2*2, r2*2),
                      int(base2*16), int(25*16))

        # ── wave ring ──
        r3 = R * 0.60
        wave_path = QPainterPath()
        for i, wv in enumerate(self._wave):
            angle_rad = math.radians(i * (360 / len(self._wave)))
            wr = r3 + wv * 8
            wx = cx + wr * math.cos(angle_rad)
            wy = cy + wr * math.sin(angle_rad)
            if i == 0: wave_path.moveTo(wx, wy)
            else: wave_path.lineTo(wx, wy)
        wave_path.closeSubpath()
        wave_pen = QPen(QColor(col.red(), col.green(), col.blue(), 120), 1)
        p.setPen(wave_pen); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(wave_path)

        # ── hexagon ──
        hex_r = R * 0.42
        hex_path = QPainterPath()
        for i in range(6):
            ar = math.radians(60*i + self._angle*0.4)
            hx = cx + hex_r * math.cos(ar)
            hy = cy + hex_r * math.sin(ar)
            if i==0: hex_path.moveTo(hx, hy)
            else: hex_path.lineTo(hx, hy)
        hex_path.closeSubpath()
        p.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), int(25+15*self._pulse))))
        p.setPen(QPen(col, 1.5))
        p.drawPath(hex_path)

        # ── core gradient fill ──
        core_r = R * 0.30
        grad = QRadialGradient(cx, cy, core_r)
        grad.setColorAt(0, QColor(col.red(), col.green(), col.blue(), int(200+55*self._pulse)))
        grad.setColorAt(0.5, QColor(col.red(), col.green(), col.blue(), 80))
        grad.setColorAt(1, QColor(0,0,0,0))
        p.setBrush(QBrush(grad)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), core_r, core_r)

        # ── center dot ──
        p.setBrush(QBrush(QColor(255,255,255,int(220+35*self._pulse))))
        p.drawEllipse(QPointF(cx, cy), 5, 5)

        # ── status text ──
        p.setPen(QPen(QColor(col.red(), col.green(), col.blue(), 180)))
        p.setFont(QFont("Consolas", 7, QFont.Weight.Bold))
        p.drawText(QRectF(cx-50, cy+R*0.78, 100, 14),
                   Qt.AlignmentFlag.AlignCenter, self._status)
        p.end()


# ══════════════════════════════════════════════
#  HEXAGON GRID BACKGROUND
# ══════════════════════════════════════════════
class HexGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._alpha = 0.0
        self._fade_in = True
        t = QTimer(self); t.timeout.connect(self._tick); t.start(50)

    def _tick(self):
        if self._fade_in:
            self._alpha = min(1.0, self._alpha + 0.02)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        hex_size = 28
        w, h = self.width(), self.height()
        pen = QPen(QColor(0, 180, 80, int(18 * self._alpha)), 0.5)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        cols = int(w / (hex_size * 1.5)) + 3
        rows = int(h / (hex_size * 1.732)) + 3
        for row in range(-1, rows):
            for col in range(-1, cols):
                cx = col * hex_size * 1.5
                cy = row * hex_size * 1.732 + (col % 2) * hex_size * 0.866
                path = QPainterPath()
                for i in range(6):
                    ar = math.radians(60*i+30)
                    x = cx + hex_size * 0.85 * math.cos(ar)
                    y = cy + hex_size * 0.85 * math.sin(ar)
                    if i==0: path.moveTo(x, y)
                    else: path.lineTo(x, y)
                path.closeSubpath()
                p.drawPath(path)
        p.end()


# ══════════════════════════════════════════════
#  SIGNAL BAR WIDGET
# ══════════════════════════════════════════════
class SignalBar(QWidget):
    def __init__(self, label, color, parent=None):
        super().__init__(parent)
        self.label = label
        self.color = color
        self._val = 0.0
        self._tgt = 0.4
        self.setFixedHeight(20)
        self.setMinimumWidth(150)
        t = QTimer(self); t.timeout.connect(self._tick); t.start(60)

    def set_value(self, v): self._tgt = max(0.0, min(1.0, v))

    def _tick(self):
        import random
        self._val += (self._tgt - self._val) * 0.12
        self._val += random.uniform(-0.004, 0.004)
        self._val = max(0.0, min(1.0, self._val))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        # track
        p.setBrush(QBrush(QColor(0,40,20,160)))
        p.setPen(QPen(QColor(0,100,50,100), 1))
        p.drawRoundedRect(0, 3, w, h-6, 3, 3)
        # fill
        fw = int((w-2)*self._val)
        if fw > 0:
            g = QLinearGradient(0,0,fw,0)
            g.setColorAt(0, QColor(self.color.red(), self.color.green(), self.color.blue(), 80))
            g.setColorAt(1, self.color)
            p.setBrush(QBrush(g)); p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(1, 4, fw, h-8, 2, 2)
        # label
        p.setPen(QPen(QColor(150,255,180)))
        p.setFont(QFont("Consolas", 7, QFont.Weight.Bold))
        p.drawText(5, 0, w-5, h, Qt.AlignmentFlag.AlignVCenter, self.label)
        p.setPen(QPen(self.color))
        p.drawText(0, 0, w-4, h, Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignRight,
                   f"{int(self._val*100)}%")
        p.end()


# ══════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════
class NexusHUD(QMainWindow):

    APP_NAME = "NEXUS"
    TAGLINE  = "Neural EXtended Understanding System"

    def __init__(self, brain, voice, dispatcher):
        super().__init__()
        self.brain = brain
        self.voice = voice
        self.dispatcher = dispatcher
        self._voice_on = True
        self._listen_worker = None
        self._proc_worker = None

        self._init_window()
        self._build_ui()
        self._start_telemetry()
        self._start_listening()

    # ── window setup ──
    def _init_window(self):
        self.setWindowTitle(f"{self.APP_NAME} — Advanced Intelligence System")
        self.setMinimumSize(1120, 740)
        self.setStyleSheet("""
            QMainWindow, QWidget#root {
                background-color: #030d08;
            }
            QScrollBar:vertical {
                background: #021008; width: 5px; border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #00aa55; border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

    # ── full UI build ──
    def _build_ui(self):
        root = QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # hexagon background
        self._hex = HexGrid(root)
        self._hex.setGeometry(root.rect())
        self._hex.lower()

        main_layout.addWidget(self._make_header())
        body = QHBoxLayout()
        body.setContentsMargins(14,10,14,10)
        body.setSpacing(12)
        body.addWidget(self._make_left())
        body.addWidget(self._make_center(), stretch=3)
        body.addWidget(self._make_right())
        main_layout.addLayout(body)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self,"_hex"):
            self._hex.setGeometry(self.centralWidget().rect())

    # ── HEADER ──
    def _make_header(self):
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #010d04, stop:0.5 #021a0a, stop:1 #010d04);
                border-bottom: 1px solid #004d20;
            }
        """)
        row = QHBoxLayout(bar); row.setContentsMargins(20,0,20,0)

        name_lbl = QLabel(self.APP_NAME)
        name_lbl.setStyleSheet("""
            color: #00ff80; font-family: Consolas; font-size: 26px;
            font-weight: bold; letter-spacing: 10px;
        """)
        sub_lbl = QLabel(self.TAGLINE)
        sub_lbl.setStyleSheet("color: #1a5c36; font-size: 8px; font-family: Consolas; letter-spacing: 3px;")
        col = QVBoxLayout(); col.setSpacing(0)
        col.addWidget(name_lbl); col.addWidget(sub_lbl)
        row.addLayout(col); row.addStretch()

        self._status_lbl = QLabel("● ONLINE")
        self._status_lbl.setStyleSheet("color:#00ff80;font-family:Consolas;font-size:10px;letter-spacing:2px;")
        row.addWidget(self._status_lbl)

        self._mic_btn = QPushButton("🎤  MIC: ON")
        self._mic_btn.setFixedSize(120, 34)
        self._mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._mic_btn.setStyleSheet(self._bs("#003315","#00aa55"))
        self._mic_btn.clicked.connect(self._toggle_voice)
        row.addWidget(self._mic_btn)

        clr_btn = QPushButton("⟳  RESET")
        clr_btn.setFixedSize(100, 34)
        clr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clr_btn.setStyleSheet(self._bs("#001a1a","#007766"))
        clr_btn.clicked.connect(self._clear)
        row.addWidget(clr_btn)
        return bar

    # ── LEFT PANEL ──
    def _make_left(self):
        pnl = QFrame(); pnl.setFixedWidth(210)
        pnl.setStyleSheet("QFrame{background:rgba(0,25,12,0.65);border:1px solid #003a18;border-radius:10px;}")
        lay = QVBoxLayout(pnl); lay.setContentsMargins(10,14,10,14); lay.setSpacing(10)

        self._orb = CentralOrb()
        lay.addWidget(self._orb, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._orb.clicked.connect(self._toggle_voice)

        lay.addWidget(self._sec_lbl("SYSTEM METRICS"))

        self._b_cpu = SignalBar("CPU   ", QColor(0,255,130))
        self._b_ram = SignalBar("RAM   ", QColor(0,220,100))
        self._b_net = SignalBar("NET   ", QColor(0,190,80))
        self._b_ai  = SignalBar("CORE  ", QColor(0,240,150))
        for b in [self._b_cpu, self._b_ram, self._b_net, self._b_ai]:
            lay.addWidget(b)

        lay.addStretch()
        lay.addWidget(self._sec_lbl("ACTIVE MODULES"))

        mods = ["WEB SEARCH","SYSTEM CTRL","CAMERA","FILE OPS",
                "WHATSAPP","EMAIL","MEMORY","DATE/TIME"]
        for m in mods:
            l = QLabel(f"  ▸ {m}")
            l.setStyleSheet("color:#1a5c36;font-size:8px;font-family:Consolas;")
            lay.addWidget(l)
        return pnl

    # ── CENTER PANEL ──
    def _make_center(self):
        pnl = QFrame()
        pnl.setStyleSheet("QFrame{background:rgba(0,18,8,0.75);border:1px solid #003a18;border-radius:10px;}")
        lay = QVBoxLayout(pnl); lay.setContentsMargins(16,14,16,14); lay.setSpacing(10)

        lay.addWidget(self._sec_lbl("CONVERSATION INTERFACE"))

        self._chat = QTextEdit()
        self._chat.setReadOnly(True)
        self._chat.setStyleSheet("""
            QTextEdit {
                background: rgba(0,12,5,0.9);
                color: #80ffb0;
                font-family: Consolas;
                font-size: 12px;
                border: 1px solid #002a10;
                border-radius: 8px;
                padding: 12px;
                selection-background-color: #004d20;
            }
        """)
        lay.addWidget(self._chat)

        inp_row = QHBoxLayout(); inp_row.setSpacing(8)
        self._inp = QLineEdit()
        self._inp.setPlaceholderText("Input command or speak to NEXUS...")
        self._inp.setFixedHeight(42)
        self._inp.setStyleSheet("""
            QLineEdit {
                background: rgba(0,20,10,0.95);
                color: #00ff80;
                font-family: Consolas;
                font-size: 12px;
                border: 1px solid #005522;
                border-radius: 8px;
                padding: 4px 14px;
            }
            QLineEdit:focus { border: 1px solid #00cc55; }
        """)
        self._inp.returnPressed.connect(self._send)
        inp_row.addWidget(self._inp)

        go = QPushButton("EXECUTE ▶")
        go.setFixedSize(110, 42)
        go.setCursor(Qt.CursorShape.PointingHandCursor)
        go.setStyleSheet(self._bs("#003318","#00cc55"))
        go.clicked.connect(self._send)
        inp_row.addWidget(go)
        lay.addLayout(inp_row)

        self._log("System initialized. All modules online. How can I assist?")
        return pnl

    # ── RIGHT PANEL ──
    def _make_right(self):
        pnl = QFrame(); pnl.setFixedWidth(200)
        pnl.setStyleSheet("QFrame{background:rgba(0,25,12,0.65);border:1px solid #003a18;border-radius:10px;}")
        lay = QVBoxLayout(pnl); lay.setContentsMargins(10,14,10,14); lay.setSpacing(8)

        lay.addWidget(self._sec_lbl("QUICK ACCESS"))

        cmds = [
            ("🕐  Current Time",    "What time is it?"),
            ("📅  Today's Date",    "What is today's date?"),
            ("📸  Screenshot",      "Take a screenshot"),
            ("📷  Camera",          "Take a photo"),
            ("👁  Detect Objects",  "Detect objects"),
            ("🔋  Battery",         "Battery status"),
            ("💻  System Stats",    "CPU usage"),
            ("🔊  Volume Up",       "Volume up"),
            ("🔉  Volume Down",     "Volume down"),
            ("📁  List Files",      "List files on desktop"),
            ("🧠  Recall Memory",   "Recall what you remember"),
            ("🗑  Clear Session",   "__clear__"),
        ]
        for label, cmd in cmds:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(28)
            btn.setStyleSheet(self._bs("#001a0d","#003322", fs=9))
            btn.clicked.connect(lambda _, c=cmd: self._quick(c))
            lay.addWidget(btn)

        lay.addStretch()

        self._clock = QLabel("00:00:00")
        self._clock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._clock.setStyleSheet("""
            color:#00ff80; font-family:Consolas;
            font-size:22px; font-weight:bold; letter-spacing:4px;
        """)
        lay.addWidget(self._clock)

        self._dateline = QLabel("")
        self._dateline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dateline.setStyleSheet("color:#1a5c36;font-size:8px;font-family:Consolas;")
        lay.addWidget(self._dateline)

        clk = QTimer(self); clk.timeout.connect(self._tick_clock); clk.start(1000)
        self._tick_clock()
        return pnl

    # ── helpers ──
    def _sec_lbl(self, txt):
        l = QLabel(txt)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setStyleSheet("color:#1a5c36;font-size:8px;font-family:Consolas;letter-spacing:2px;")
        return l

    def _bs(self, bg, border, fs=10):
        return f"""
            QPushButton {{
                background:{bg}; color:#00cc66;
                border:1px solid {border}; border-radius:5px;
                font-family:Consolas; font-size:{fs}px;
                font-weight:bold; letter-spacing:1px;
            }}
            QPushButton:hover {{ background:{border}; color:#ffffff; }}
            QPushButton:pressed {{ background:#000a05; }}
        """

    def _log(self, text: str, role="system"):
        colors = {"user":"#336644","nexus":"#00aa55","skill":"#00cc77","system":"#005522"}
        labels = {"user":"▸ YOU","nexus":f"◈ {self.APP_NAME}","skill":"⚡ MODULE","system":"◉ SYS"}
        c = colors.get(role,"#336644"); lbl = labels.get(role,"◉")
        self._chat.append(
            f'<span style="color:{c};font-family:Consolas;font-size:9px;">{lbl}</span>'
            f'<br><span style="color:#80ffb0;font-family:Consolas;font-size:12px;">{text}</span><br>'
        )

    def _tick_clock(self):
        now = datetime.now()
        self._clock.setText(now.strftime("%H:%M:%S"))
        self._dateline.setText(now.strftime("%a, %b %d %Y"))

    def _start_telemetry(self):
        import psutil, random
        def _upd():
            try:
                self._b_cpu.set_value(psutil.cpu_percent()/100)
                self._b_ram.set_value(psutil.virtual_memory().percent/100)
                self._b_net.set_value(random.uniform(0.1,0.55))
                self._b_ai.set_value(random.uniform(0.35,0.9))
            except Exception: pass
        t = QTimer(self); t.timeout.connect(_upd); t.start(2000); _upd()

    def _set_status(self, s: str):
        self._orb.set_status(s)
        clr = {"STANDBY":"#00ff80","LISTENING":"#ffff44","PROCESSING":"#ffaa00","SPEAKING":"#00ffcc"}.get(s,"#00ff80")
        self._status_lbl.setText(f"● {s}")
        self._status_lbl.setStyleSheet(f"color:{clr};font-family:Consolas;font-size:10px;letter-spacing:2px;")

    def _start_listening(self):
        if not self._voice_on: return
        self._listen_worker = ListenWorker(self.voice)
        self._listen_worker.heard.connect(self._on_voice)
        self._listen_worker.status.connect(self._set_status)
        self._listen_worker.start()

    def _stop_listening(self):
        if self._listen_worker:
            self._listen_worker.stop()
            self._listen_worker.quit()
            self._listen_worker = None

    def _toggle_voice(self):
        self._voice_on = not self._voice_on
        if self._voice_on:
            self._mic_btn.setText("🎤  MIC: ON")
            self._start_listening()
        else:
            self._mic_btn.setText("🔇  MIC: OFF")
            self._stop_listening()
            self._set_status("STANDBY")

    def _on_voice(self, text: str):
        self._inp.setText(text); self._process(text)

    def _send(self):
        t = self._inp.text().strip()
        if t: self._inp.clear(); self._process(t)

    def _quick(self, cmd: str):
        if cmd == "__clear__": self._clear(); return
        self._process(cmd)

    def _process(self, text: str):
        self._log(text, "user")
        self._set_status("PROCESSING")
        self._proc_worker = ProcessWorker(self.brain, self.dispatcher, text)
        self._proc_worker.done.connect(self._on_reply)
        self._proc_worker.skill_out.connect(lambda r: self._log(r,"skill"))
        self._proc_worker.status.connect(self._set_status)
        self._proc_worker.start()

    def _on_reply(self, reply: str):
        self._log(reply, "nexus")
        if self._voice_on:
            self._set_status("SPEAKING")
            threading.Thread(target=self._speak, args=(reply,), daemon=True).start()

    def _speak(self, text: str):
        self.voice.speak(text, block=True)
        self._set_status("STANDBY")

    def _clear(self):
        self._chat.clear()
        self.brain.reset()
        self._log("Session reset. Ready.", "system")

    def closeEvent(self, e):
        self._stop_listening()
        self.voice.stop()
        e.accept()
