import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class DataLoader:
    def __init__(self, data_path: str = "dataset/chat.json"):
        self.data_path = data_path
        self.messages: List[Dict[str, Any]] = []
        self.id_map: Dict[int, Dict[str, Any]] = {}
        self.index_map: Dict[int, int] = {}  # message_id -> list index
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_path):
            # Fallback path try
            alt_path = os.path.join("..", self.data_path)
            if os.path.exists(alt_path):
                self.data_path = alt_path
            else:
                raise FileNotFoundError(f"Dataset file not found at {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            self.messages = json.load(f)

        # Build lookup maps
        for idx, msg in enumerate(self.messages):
            m_id = msg["id"]
            self.id_map[m_id] = msg
            self.index_map[m_id] = idx

    def get_message_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        return self.id_map.get(message_id)

    def get_context(self, message_id: int, before_count: int = 5, after_count: int = 5) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if message_id not in self.index_map:
            return [], []

        idx = self.index_map[message_id]
        
        start_idx = max(0, idx - before_count)
        end_idx = min(len(self.messages), idx + after_count + 1)

        context_before = self.messages[start_idx:idx]
        context_after = self.messages[idx + 1:end_idx]

        return context_before, context_after

    def get_participants(self) -> List[str]:
        senders = set(m["sender"] for m in self.messages)
        return sorted(list(senders))

    def get_stats(self) -> Dict[str, Any]:
        if not self.messages:
            return {}
        
        timestamps = [m["timestamp"] for m in self.messages]
        start_time = min(timestamps)
        end_time = max(timestamps)
        
        return {
            "total_messages": len(self.messages),
            "participants_count": len(self.get_participants()),
            "participants": self.get_participants(),
            "date_range": f"{start_time[:10]} to {end_time[:10]}"
        }
