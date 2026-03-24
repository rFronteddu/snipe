import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Memory")

class Memory:
    def __init__(self, filename="data/memory.json", threshold=15):
        self.filename = filename
        self.threshold = threshold  # Max turns before summarizing
        self.data = {
            "chat_history": [],
            "context_summary": "",
            "metadata": {}
        }
        self._load()

    def _load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except (json.JSONDecodeError, ValueError):
                pass
        else:
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            self._save()

    def _save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=2)

    def append(self, key, value):
        """
        Generic append for metadata lists (e.g., 'user_interests').
        """
        if key not in self.data["metadata"]:
            self.data["metadata"][key] = []

        # Only append if it's not a duplicate
        if isinstance(self.data["metadata"][key], list):
            if value not in self.data["metadata"][key]:
                self.data["metadata"][key].append(value)
                self._save()
        else:
            logger.warning(f"Key '{key}' in metadata is not a list. Use update_metadata instead.")

    def add_chat_turn(self, role, content):
        """Adds a message turn to the history with a timestamp."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if "chat_history" not in self.data:
            self.data["chat_history"] = []

        self.data["chat_history"].append(entry)
        self._save()

    def get_recent_context(self, limit=10):
        """Returns the summary + the last N messages."""
        summary = f"SUMMARY OF PAST EVENTS: {self.data.get('context_summary', 'None')}\n\n"

        history = self.data.get("chat_history", [])[-limit:]
        formatted = []
        for turn in history:
            role = "User" if turn["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {turn['content']}")

        return summary + "RECENT CONVERSATION:\n" + "\n".join(formatted)

    def summarize_if_needed(self, llm, summary_template):
        """If history exceeds threshold, condense the oldest part."""
        history = self.data.get("chat_history", [])

        if len(history) < self.threshold:
            return

        # Take the oldest 10 turns to summarize
        to_summarize = history[:10]
        # Keep the rest as active history
        self.data["chat_history"] = history[10:]

        text_to_condense = "\n".join([f"{t['role']}: {t['content']}" for t in to_summarize])

        prompt = summary_template.format(
            existing_summary=self.data.get('context_summary', 'None'),
            new_lines=text_to_condense
        )

        new_summary = llm.generate(prompt)
        self.data["context_summary"] = new_summary
        self._save()
        print("--- MEMORY SUMMARIZED ---")

    def clear_history(self):
        """Clears only the chat history while keeping metadata."""
        self.data["chat_history"] = []
        self._save()

    def update_metadata(self, key, value):
        """Store facts about the user (e.g., 'name': 'Dave')."""
        if "metadata" not in self.data:
            self.data["metadata"] = {}
        self.data["metadata"][key] = value
        self._save()

    def get_metadata(self, key, default=None):
        return self.data.get("metadata", {}).get(key, default)