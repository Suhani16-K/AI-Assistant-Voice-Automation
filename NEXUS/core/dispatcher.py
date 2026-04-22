"""
core/dispatcher.py
NEXUS — Command Dispatcher
"""


class Dispatcher:
    def __init__(self):
        self._modules = {}
        self._load()

    def _load(self):
        try:
            from skills.web_ops import WebOps
            w = WebOps()
            self._reg("web_search", w.search, ["search for","google","look up","search"])
            self._reg("open_site", w.open_site, ["open","go to","visit","launch website"])
            self._reg("youtube", w.open_youtube, ["youtube","play on youtube"])
        except Exception as e:
            print(f"[Dispatcher] web_ops: {e}")

        try:
            from skills.system_ops import SystemOps
            s = SystemOps()
            self._reg("vol_up",    s.volume_up,      ["volume up","increase volume","louder"])
            self._reg("vol_down",  s.volume_down,    ["volume down","decrease volume","quieter"])
            self._reg("mute",      s.mute,           ["mute","silence"])
            self._reg("bright_up", s.brightness_up,  ["brightness up","increase brightness"])
            self._reg("bright_dn", s.brightness_down,["brightness down","decrease brightness"])
            self._reg("open_app",  s.open_app,       ["open app","launch","start app"])
            self._reg("battery",   s.battery_status, ["battery","battery level","battery status"])
            self._reg("cpu",       s.cpu_usage,      ["cpu","processor","ram usage","cpu usage"])
            self._reg("lock",      s.lock_screen,    ["lock screen","lock computer"])
        except Exception as e:
            print(f"[Dispatcher] system_ops: {e}")

        try:
            from skills.screenshot_ops import ScreenshotOps
            sc = ScreenshotOps()
            self._reg("screenshot", sc.take_screenshot, ["screenshot","take screenshot","capture screen"])
        except Exception as e:
            print(f"[Dispatcher] screenshot_ops: {e}")

        try:
            from skills.file_ops import FileOps
            f = FileOps()
            self._reg("create_file", f.create_file, ["create file","new file","make file"])
            self._reg("read_file",   f.read_file,   ["read file","open file","show file"])
            self._reg("list_files",  f.list_files,  ["list files","show files","what files"])
            self._reg("delete_file", f.delete_file, ["delete file","remove file"])
        except Exception as e:
            print(f"[Dispatcher] file_ops: {e}")

        try:
            from skills.datetime_ops import DateTimeOps
            dt = DateTimeOps()
            self._reg("get_time",  dt.get_time,    ["what time","current time","time now"])
            self._reg("get_date",  dt.get_date,    ["what date","today's date","current date","what day"])
            self._reg("reminder",  dt.set_reminder,["remind me","set reminder","set alarm"])
        except Exception as e:
            print(f"[Dispatcher] datetime_ops: {e}")

        try:
            from skills.camera_skill import CameraSkill
            cam = CameraSkill()
            self._reg("photo",   cam.take_photo,     ["take photo","take picture","capture photo","click photo"])
            self._reg("detect",  cam.detect_objects, ["detect objects","what do you see","object detection"])
        except Exception as e:
            print(f"[Dispatcher] camera_skill: {e}")

        try:
            from skills.whatsapp_skill import WhatsAppSkill
            wa = WhatsAppSkill()
            self._reg("whatsapp", wa.send_message, ["send whatsapp","whatsapp message","message on whatsapp"])
        except Exception as e:
            print(f"[Dispatcher] whatsapp: {e}")

        try:
            from skills.email_ops import EmailOps
            em = EmailOps()
            self._reg("email", em.send_email, ["send email","compose email","email to"])
        except Exception as e:
            print(f"[Dispatcher] email_ops: {e}")

        try:
            from skills.memory_ops import MemoryOps
            mo = MemoryOps()
            self._reg("remember", mo.remember, ["remember","don't forget","keep in mind"])
            self._reg("recall",   mo.recall,   ["recall","what did i tell you","do you remember"])
        except Exception as e:
            print(f"[Dispatcher] memory_ops: {e}")

    def _reg(self, name, func, triggers):
        self._modules[name] = {"func": func, "triggers": [t.lower() for t in triggers]}

    def dispatch(self, text: str):
        t = text.lower().strip()
        for name, mod in self._modules.items():
            for trigger in mod["triggers"]:
                if trigger in t:
                    try:
                        return mod["func"](text), name
                    except Exception as e:
                        return f"Module '{name}' error: {e}", name
        return None, None

    def list_modules(self):
        return list(self._modules.keys())
