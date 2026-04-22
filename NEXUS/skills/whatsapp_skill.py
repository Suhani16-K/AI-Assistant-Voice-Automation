"""skills/whatsapp_skill.py"""
import re

class WhatsAppSkill:
    def send_message(self, q) -> str:
        try:
            import pywhatkit as kit
            phone = re.search(r'\+?\d[\d\s\-]{8,14}', q)
            msg = re.search(r'(?:saying|message|say|tell them)\s+["\']?(.+)["\']?', q, re.I)
            if not phone: return "Please provide a phone number."
            num = phone.group().replace(" ","").replace("-","")
            if not num.startswith("+"): num = "+91" + num
            text = msg.group(1) if msg else "Hello from NEXUS!"
            kit.sendwhatmsg_instantly(num, text, wait_time=15, tab_close=True)
            return f"Message sent to {num}."
        except Exception as e: return f"WhatsApp error: {e}"
