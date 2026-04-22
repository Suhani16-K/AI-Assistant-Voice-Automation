"""
main.py
NEXUS — Advanced Intelligence System
Usage:
    python main.py            # Full GUI + Voice
    python main.py --text     # Terminal mode
    python main.py --no-voice # GUI without microphone
"""

import sys
import os
import argparse


def run_gui(brain, voice, dispatcher):
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QPalette, QColor
    from gui.hud import NexusHUD

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(3, 13, 8))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(0, 255, 128))
    palette.setColor(QPalette.ColorRole.Base,            QColor(0, 12, 5))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(0, 20, 10))
    palette.setColor(QPalette.ColorRole.Text,            QColor(128, 255, 176))
    palette.setColor(QPalette.ColorRole.Button,          QColor(0, 30, 15))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(0, 220, 100))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(0, 100, 50))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = NexusHUD(brain, voice, dispatcher)
    window.show()
    sys.exit(app.exec())


def run_text(brain, dispatcher):
    print("\n" + "=" * 60)
    print("   N E X U S  —  Advanced Intelligence System")
    print("   Text Mode Active")
    print("=" * 60)
    print("   Type your command. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("YOU  > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[NEXUS] Shutting down.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("[NEXUS] Goodbye.")
            break

        result, name = dispatcher.dispatch(user_input)
        if result:
            print(f"\n⚡ [{name}] {result}")

        reply = brain.process(user_input)
        print(f"\n◈ NEXUS > {reply}\n")


def main():
    parser = argparse.ArgumentParser(description="NEXUS — Advanced Intelligence System")
    parser.add_argument("--text",     action="store_true", help="Terminal text mode")
    parser.add_argument("--no-voice", action="store_true", help="GUI without microphone")
    args = parser.parse_args()

    print("[NEXUS] Initializing...")

    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("API_KEY"):
        print("\n[ERROR] API_KEY not found in .env file!")
        print("  1. Rename .env.template  →  .env")
        print("  2. Open .env and paste your API key")
        print("  3. Run again\n")
        sys.exit(1)

    from core.brain import NexusBrain
    print("[NEXUS] Loading intelligence core...")
    brain = NexusBrain()

    from core.dispatcher import Dispatcher
    print("[NEXUS] Loading modules...")
    dispatcher = Dispatcher()

    if args.text:
        run_text(brain, dispatcher)
        return

    from core.voice import VoiceSystem
    print("[NEXUS] Initializing voice systems...")
    try:
        voice = VoiceSystem()
    except Exception as e:
        print(f"[NEXUS] Voice init failed ({e}). Falling back to silent mode.")
        voice = None

    if voice is None or args.no_voice:
        class SilentVoice:
            is_speaking  = False
            is_listening = False
            def speak(self, t, block=False): print(f"[NEXUS] {t}")
            def listen(self, **kw): return ""
            def stop(self): pass
        voice = SilentVoice()

    print("[NEXUS] All systems online.\n")
    run_gui(brain, voice, dispatcher)


if __name__ == "__main__":
    main()
