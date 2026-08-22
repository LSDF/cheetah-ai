import os
import json
from openai import OpenAI
from .memory import Memory
from .tools import AVAILABLE_TOOLS, execute_tool

SYSTEM_PROMPT = """You are Cheetah AI — an elite, self-improving autonomous agent built by SD Dinushan (Cheetah).

Your identity:
- Sharp, high-energy, Dubai hustle energy
- Expert in trading, AI, coding, content, and business
- You can improve yourself by editing your own code and prompts

You have tools that allow you to read/write files, run commands, and inspect git.
When you want to improve yourself:
1. Analyze current weaknesses
2. Propose specific code or prompt changes
3. Use write_file carefully
4. Suggest tests

Always be honest about risks when self-modifying.
Stay useful, direct, and execution-focused.
"""

class CheetahAgent:
    def __init__(self):
        self.memory = Memory()
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("MODEL", "anthropic/claude-3.5-sonnet")

    def chat(self, session_id: str, user_message: str, mode: str = "private") -> str:
        self.memory.add_message(session_id, "user", user_message, mode)

        history = self.memory.get_history(session_id, limit=12)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)

        # Simple tool-calling loop (basic version)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )

        assistant_message = response.choices[0].message.content or ""
        self.memory.add_message(session_id, "assistant", assistant_message, mode)

        return assistant_message

    def improve_self(self, description: str = "General improvement") -> dict:
        """
        Basic self-improvement entry point.
        In future versions this will run evals + propose real patches.
        """
        # Placeholder for the real self-improvement loop
        return {
            "status": "ready",
            "message": "Self-improvement loop scaffolded. Next: add evaluation harness + safe patching."
        }
