import os
import subprocess
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent

def read_file(path: str) -> str:
    """Read a file relative to project root."""
    full = PROJECT_ROOT / path
    if not full.exists():
        return f"Error: File not found: {path}"
    try:
        return full.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path: str, content: str) -> str:
    """Write content to a file (self-modification tool)."""
    full = PROJECT_ROOT / path
    try:
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    full = PROJECT_ROOT / directory
    if not full.exists():
        return f"Directory not found: {directory}"
    files = []
    for p in full.rglob("*"):
        if p.is_file() and ".git" not in str(p) and "__pycache__" not in str(p):
            files.append(str(p.relative_to(PROJECT_ROOT)))
    return "\n".join(files[:100]) or "No files found"

def run_command(cmd: str) -> str:
    """Run a shell command (sandboxed as much as possible)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return output[:3000] if output else "Command executed with no output"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {e}"

def git_status() -> str:
    return run_command("git status --short")

def git_diff() -> str:
    return run_command("git diff")

AVAILABLE_TOOLS = {
    "read_file": {
        "description": "Read the content of a file in the project",
        "parameters": {"path": "string"}
    },
    "write_file": {
        "description": "Write or overwrite a file (use carefully for self-improvement)",
        "parameters": {"path": "string", "content": "string"}
    },
    "list_files": {
        "description": "List project files",
        "parameters": {"directory": "string (optional)"}
    },
    "run_command": {
        "description": "Run a shell command in the project directory",
        "parameters": {"cmd": "string"}
    },
    "git_status": {
        "description": "Show git status",
        "parameters": {}
    },
    "git_diff": {
        "description": "Show current git diff",
        "parameters": {}
    }
}

def execute_tool(name: str, args: dict) -> str:
    if name == "read_file":
        return read_file(args.get("path", ""))
    elif name == "write_file":
        return write_file(args.get("path", ""), args.get("content", ""))
    elif name == "list_files":
        return list_files(args.get("directory", "."))
    elif name == "run_command":
        return run_command(args.get("cmd", ""))
    elif name == "git_status":
        return git_status()
    elif name == "git_diff":
        return git_diff()
    return f"Unknown tool: {name}"
