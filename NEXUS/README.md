# NEXUS — Advanced Intelligence System

> *Neural EXtended Understanding System*

A voice-controlled AI assistant with a futuristic green HUD interface, modular skill system, and real-time system telemetry.

---

## Features

| Module | Capability |
|---|---|
| Intelligence Core | Natural language understanding with memory |
| Voice I/O | Microphone input + Text-to-speech output |
| HUD Interface | Green circular orb, hexagon grid, telemetry bars |
| Web | Google search, open websites, YouTube |
| System | Volume, brightness, apps, battery, CPU/RAM |
| Vision | Screenshot, camera capture, object detection (YOLOv8) |
| Files | Create, read, list, delete files |
| WhatsApp | Automated messaging |
| Email | Gmail sending |
| Memory | Persistent cross-session memory |
| DateTime | Time, date, reminders |

---

## Setup

### Step 1 — Python
Install Python 3.10+ from https://python.org  
✅ Check **"Add Python to PATH"** during install.

### Step 2 — Dependencies

Open terminal/CMD in this folder:

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

> **PyAudio fix on Windows (if pip install fails):**
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### Step 3 — API Key

1. Rename `.env.template` → `.env`
2. Open `.env` and add your key:

```
API_KEY=your_key_here
```

### Step 4 — Run

```bash
python main.py              # GUI + Voice (full)
python main.py --no-voice   # GUI only
python main.py --text       # Terminal only
```

---

## Voice Commands

| Say | Action |
|---|---|
| "Search for quantum computing" | Google search |
| "Open YouTube" | Opens YouTube |
| "Take a screenshot" | Saves to assets/ |
| "Take a photo" | Camera capture |
| "Detect objects" | YOLOv8 detection |
| "Volume up / down" | System volume |
| "Battery status" | Battery info |
| "CPU usage" | CPU + RAM stats |
| "What time is it?" | Current time |
| "Remind me in 10 minutes to drink water" | Sets reminder |
| "Remember that my project deadline is Friday" | Saves to memory |
| "Recall what you remember" | Reads memory |
| "Create file named report" | Creates file on Desktop |

---

## Project Structure

```
NEXUS/
├── main.py               ← Entry point
├── requirements.txt
├── .env.template         ← Copy to .env
│
├── core/
│   ├── brain.py          ← Intelligence core
│   ├── voice.py          ← Voice I/O
│   ├── memory.py         ← Persistent memory
│   └── dispatcher.py     ← Command routing
│
├── gui/
│   └── hud.py            ← Full HUD interface
│
├── skills/
│   ├── web_ops.py
│   ├── system_ops.py
│   ├── screenshot_ops.py
│   ├── camera_skill.py
│   ├── file_ops.py
│   ├── datetime_ops.py
│   ├── whatsapp_skill.py
│   ├── email_ops.py
│   └── memory_ops.py
│
└── assets/               ← Auto-created at runtime
```

---

## Troubleshooting

**PyAudio error on Windows:**
```bash
pip install pipwin && pipwin install pyaudio
```

**No microphone / voice errors:**
```bash
python main.py --no-voice
```

**First-time object detection** auto-downloads model (~6MB), needs internet.
