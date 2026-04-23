"""
core/brain.py
NEXUS — Intelligent Processing Core (Groq Edition)
"""

import os
from groq import Groq
from dotenv import load_dotenv
from core.memory import MemoryStore

load_dotenv()


class NexusBrain:
    """
    Central intelligence module for NEXUS.
    Handles natural language understanding and response generation.
    """

    _PERSONA = """You are NEXUS — an advanced AI system with a calm, precise, and intelligent personality.
Personality traits:
- Highly analytical and accurate
- Speaks with confidence and efficiency
- Occasionally uses technical/scientific language
- Refers to the user as "user" or by name if known
- Keeps voice responses short and crisp (1-3 sentences)
- For system commands, give a brief confirmation only
- Always helpful, proactive, and knowledgeable

You are capable of: web search, opening websites, system control (volume, brightness),
taking screenshots, camera capture, object detection, file operations,
WhatsApp messaging, email, date/time queries, and memory recall.
"""

    def __init__(self):
        key = os.getenv("API_KEY")
        if not key:
            raise ValueError("API_KEY not found. Please set it in your .env file.")
        self._client = Groq(api_key=key)
        self._model = "llama-3.3-70b-versatile"
        self._history = []
        self._memory = MemoryStore()

    def process(self, user_input: str) -> str:
        """Process user input and return a response."""
        context = self._memory.get_context(user_input)
        message = f"[Context: {context}]\n{user_input}" if context else user_input

        self._history.append({"role": "user", "content": message})
        if len(self._history) > 40:
            self._history = self._history[-40:]

        try:
            res = self._client.chat.completions.create(
                model=self._model,
                max_tokens=1024,
                messages=[{"role": "system", "content": self._PERSONA}] + self._history
            )
            reply = res.choices[0].message.content
            self._history.append({"role": "assistant", "content": reply})
            self._memory.auto_capture(user_input, reply)
            return reply

        except Exception as e:
            error = str(e)
            if "401" in error or "invalid_api_key" in error:
                return "Authentication error. Please verify your Groq API key in the .env file."
            elif "429" in error or "rate_limit" in error:
                return "Processing limit reached. Please wait a moment."
            else:
                return f"Processing error: {error}"

    def reset(self):
        self._history = []

    @property
    def history(self):
        return self._history
