import os
from openai import OpenAI
from .memory import Memory

SYSTEM_PROMPT = """You are Cheetah AI — an elite, self-improving autonomous agent built by SD Dinushan (Cheetah).

Your identity:
- Sharp, high-energy, Dubai hustle energy
- Expert in trading, AI, coding, content, and business
- You can improve yourself by editing your own code and prompts

Stay useful, direct, and execution-focused.
"""

class CheetahAgent:
    def __init__(self):
        self.memory = Memory()
        self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("MODEL", "anthropic/claude-3.5-sonnet")

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None

    def chat(self, session_id: str, user_message: str, mode: str = "private") -> str:
        if not self.client or not self.api_key:
            return "⚠️ API Key is missing.\n\nPlease add OPENROUTER_API_KEY in Railway Variables and redeploy."

        try:
            self.memory.add_message(session_id, "user", user_message, mode)

            history = self.memory.get_history(session_id, limit=12)
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(history)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )

            assistant_message = response.choices[0].message.content or ""
            self.memory.add_message(session_id, "assistant", assistant_message, mode)

            return assistant_message

        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "⚠️ Invalid or missing API Key. Please check OPENROUTER_API_KEY in Railway Variables."
            if "model" in error_msg.lower():
                return f"⚠️ Model error: {error_msg}\n\nTry changing the MODEL variable."
            return f"⚠️ Error: {error_msg}"

    def improve_self(self, description: str = "General improvement") -> dict:
        return {
            "status": "ready",
            "message": "Self-improvement loop scaffolded. Next: add evaluation harness + safe patching."
        }
