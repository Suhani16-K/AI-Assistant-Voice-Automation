"""skills/screenshot_ops.py"""
import pyautogui, os
from datetime import datetime

class ScreenshotOps:
    def __init__(self):
        os.makedirs("assets/screenshots", exist_ok=True)

    def take_screenshot(self, q="") -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp = f"assets/screenshots/capture_{ts}.png"
        try:
            pyautogui.screenshot().save(fp)
            return f"Screenshot saved: {fp}"
        except Exception as e:
            return f"Screenshot failed: {e}"
