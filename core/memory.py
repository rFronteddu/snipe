import json
import os

class Memory:
    def __init__(self, filename="data/memory.json"):
        self.filename = filename
        self.data = {}

        # Load existing memory if file exists
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = {}
        else:
            # Ensure folder exists
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            self._save()

    def _save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self._save()

    def append(self, key, value):
        """
        Append a value to a list in memory.
        """
        if key not in self.data:
            self.data[key] = []
        if value not in self.data[key]:
            self.data[key].append(value)
        self._save()

    def remove(self, key, value):
        """
        Remove a value from a list in memory.
        """
        if key in self.data and value in self.data[key]:
            self.data[key].remove(value)
            self._save()
