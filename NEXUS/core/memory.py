"""
core/memory.py
NEXUS — Persistent Memory Storage
"""

import json
import os
from datetime import datetime


class MemoryStore:
    _FILE = "assets/memory.json"

    def __init__(self):
        os.makedirs("assets", exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self._FILE):
            try:
                with open(self._FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"facts": [], "preferences": {}}

    def _save(self):
        with open(self._FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def store(self, key: str, value: str):
        self._data["preferences"][key] = {"value": value, "ts": datetime.now().isoformat()}
        self._save()

    def fetch(self, key: str) -> str:
        item = self._data["preferences"].get(key)
        return item["value"] if item else None

    def add_fact(self, fact: str):
        self._data["facts"].append({"fact": fact, "ts": datetime.now().isoformat()})
        if len(self._data["facts"]) > 100:
            self._data["facts"] = self._data["facts"][-100:]
        self._save()

    def get_context(self, query: str) -> str:
        q = query.lower()
        relevant = []
        for k, v in self._data["preferences"].items():
            if k.lower() in q:
                relevant.append(f"{k}: {v['value']}")
        for f in self._data["facts"][-5:]:
            relevant.append(f["fact"])
        return "; ".join(relevant[:4]) if relevant else ""

    def get_all(self) -> list:
        return self._data["facts"]

    def clear(self):
        self._data = {"facts": [], "preferences": {}}
        self._save()

    def auto_capture(self, user_input: str, response: str):
        triggers = ["my name is", "i am", "call me", "i like", "i prefer", "remember"]
        if any(t in user_input.lower() for t in triggers):
            self.add_fact(user_input[:120])
