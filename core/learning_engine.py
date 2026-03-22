"""
Self-Learning Memory Engine
Stores and reuses successful column mappings
"""

import json
import os
from datetime import datetime


class LearningEngine:
    """Store and retrieve learned column mappings"""

    def __init__(self, path="memory/knowledge.json"):
        """Initialize learning engine with persistent memory"""
        self.path = path

        if not os.path.exists("memory"):
            os.makedirs("memory")

        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({"mappings": {}, "history": []}, f)

        with open(self.path, "r") as f:
            self.memory = json.load(f)

    def get(self, column_name):
        """Retrieve learned mapping for a column"""
        key = column_name.lower().strip()
        return self.memory["mappings"].get(key)

    def store(self, column_name, category, confidence):
        """Store a new successful mapping"""
        key = column_name.lower().strip()

        self.memory["mappings"][key] = {
            "category": category,
            "confidence": float(confidence),
            "learned_at": datetime.now().isoformat()
        }

        # Add to history
        self.memory["history"].append({
            "column": column_name,
            "category": category,
            "confidence": float(confidence),
            "timestamp": datetime.now().isoformat()
        })

        # Persist to disk
        with open(self.path, "w") as f:
            json.dump(self.memory, f, indent=4)

    def get_all(self):
        """Get all learned mappings"""
        return self.memory["mappings"]

    def clear(self):
        """Clear all learned mappings"""
        self.memory = {"mappings": {}, "history": []}
        with open(self.path, "w") as f:
            json.dump(self.memory, f)
