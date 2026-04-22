"""skills/memory_ops.py"""
import re
from core.memory import MemoryStore

class MemoryOps:
    def __init__(self):
        self._mem = MemoryStore()

    def remember(self, q) -> str:
        m = re.search(r'remember\s+(?:that\s+)?(.+)', q, re.I)
        if m:
            self._mem.add_fact(m.group(1).strip())
            return f"Noted: '{m.group(1).strip()}'"
        return "What would you like me to remember?"

    def recall(self, q) -> str:
        facts = self._mem.get_all()
        if facts:
            return "I remember: " + "; ".join(f["fact"] for f in facts[-5:])
        return "Nothing stored in memory yet."
