"""skills/datetime_ops.py"""
import threading, re
from datetime import datetime

class DateTimeOps:
    def get_time(self, q="") -> str:
        return f"Current time: {datetime.now().strftime('%I:%M %p')}"

    def get_date(self, q="") -> str:
        return f"Today: {datetime.now().strftime('%A, %B %d, %Y')}"

    def set_reminder(self, q) -> str:
        m = re.search(r'(\d+)\s*(minute|hour|second)', q.lower())
        if m:
            n, unit = int(m.group(1)), m.group(2)
            secs = n * (60 if "minute" in unit else 3600 if "hour" in unit else 1)
            mm = re.search(r'(?:to|about|that)\s+(.+)', q.lower())
            msg = mm.group(1) if mm else "Reminder!"
            def _remind():
                import time; time.sleep(secs)
                print(f"\n🔔 REMINDER: {msg}")
            threading.Thread(target=_remind, daemon=True).start()
            return f"Reminder set for {n} {unit}(s): '{msg}'"
        return "Please specify time, e.g. 'remind me in 5 minutes to check email'."
