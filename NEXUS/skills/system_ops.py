"""skills/system_ops.py — System control"""
import os, platform, subprocess, psutil

class SystemOps:
    def __init__(self):
        self.os = platform.system()

    def volume_up(self, q="") -> str:
        if self.os=="Windows": subprocess.call(["powershell","-c","(New-Object -com wscript.shell).SendKeys([char]175)"])
        elif self.os=="Darwin": subprocess.call(["osascript","-e","set volume output volume ((output volume of (get volume settings)) + 10)"])
        else: subprocess.call(["amixer","-D","pulse","sset","Master","10%+"])
        return "Volume increased."

    def volume_down(self, q="") -> str:
        if self.os=="Windows": subprocess.call(["powershell","-c","(New-Object -com wscript.shell).SendKeys([char]174)"])
        elif self.os=="Darwin": subprocess.call(["osascript","-e","set volume output volume ((output volume of (get volume settings)) - 10)"])
        else: subprocess.call(["amixer","-D","pulse","sset","Master","10%-"])
        return "Volume decreased."

    def mute(self, q="") -> str:
        if self.os=="Windows": subprocess.call(["powershell","-c","(New-Object -com wscript.shell).SendKeys([char]173)"])
        elif self.os=="Darwin": subprocess.call(["osascript","-e","set volume output muted true"])
        else: subprocess.call(["amixer","-D","pulse","sset","Master","toggle"])
        return "Audio muted."

    def brightness_up(self, q="") -> str:
        try:
            import screen_brightness_control as sbc
            cur = sbc.get_brightness()[0]
            sbc.set_brightness(min(100, cur+10))
            return f"Brightness set to {min(100,cur+10)}%."
        except Exception as e: return f"Brightness error: {e}"

    def brightness_down(self, q="") -> str:
        try:
            import screen_brightness_control as sbc
            cur = sbc.get_brightness()[0]
            sbc.set_brightness(max(10, cur-10))
            return f"Brightness set to {max(10,cur-10)}%."
        except Exception as e: return f"Brightness error: {e}"

    def open_app(self, query: str) -> str:
        apps = {"notepad":"notepad","calculator":"calc","chrome":"start chrome",
                "firefox":"start firefox","vscode":"code","terminal":"cmd","file manager":"explorer"}
        for app, cmd in apps.items():
            if app in query.lower():
                os.system(cmd if self.os=="Windows" else cmd.replace("start ",""))
                return f"Opening {app.title()}."
        return "Which application would you like to open?"

    def battery_status(self, q="") -> str:
        b = psutil.sensors_battery()
        if b: return f"Battery at {b.percent:.0f}%, {'charging' if b.power_plugged else 'discharging'}."
        return "No battery info available."

    def cpu_usage(self, q="") -> str:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        return f"CPU: {cpu}% | RAM: {ram.percent}% ({ram.used//(1024**2)}MB / {ram.total//(1024**2)}MB)."

    def lock_screen(self, q="") -> str:
        if self.os=="Windows": os.system("rundll32.exe user32.dll,LockWorkStation")
        elif self.os=="Darwin": os.system("pmset displaysleepnow")
        else: os.system("gnome-screensaver-command -l")
        return "Screen locked."
