"""
core/voice.py
NEXUS — Voice Input/Output System
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue


class VoiceSystem:
    def __init__(self):
        self._engine = pyttsx3.init()
        self._configure()
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = 300
        self._recognizer.dynamic_energy_threshold = True
        self._recognizer.pause_threshold = 0.8
        self.is_speaking = False
        self.is_listening = False
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _configure(self):
        voices = self._engine.getProperty("voices")
        for v in voices:
            if any(x in v.name.lower() for x in ["male", "david", "mark", "george"]):
                self._engine.setProperty("voice", v.id)
                break
        self._engine.setProperty("rate", 170)
        self._engine.setProperty("volume", 0.95)

    def _worker(self):
        while True:
            text = self._queue.get()
            if text is None:
                break
            self.is_speaking = True
            self._engine.say(text)
            self._engine.runAndWait()
            self.is_speaking = False
            self._queue.task_done()

    def speak(self, text: str, block: bool = False):
        clean = text.replace("*","").replace("#","").replace("`","").replace("_"," ")
        self._queue.put(clean)
        if block:
            self._queue.join()

    def stop(self):
        self._engine.stop()

    def listen(self, timeout: int = 5, phrase_limit: int = 10) -> str:
        self.is_listening = True
        try:
            with sr.Microphone() as src:
                self._recognizer.adjust_for_ambient_noise(src, duration=0.3)
                audio = self._recognizer.listen(src, timeout=timeout, phrase_time_limit=phrase_limit)
            text = self._recognizer.recognize_google(audio)
            self.is_listening = False
            return text.strip()
        except Exception:
            self.is_listening = False
            return ""
