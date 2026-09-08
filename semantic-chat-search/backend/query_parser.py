import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List

PARTICIPANTS = ["Aman", "Priya", "Rahul", "Neha", "Ravi", "Ankit", "Simran", "Karan"]

MONTH_NAMES = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}

class QueryParser:
    def __init__(self, participants: List[str] = PARTICIPANTS):
        self.participants = participants

    def parse(self, query: str, reference_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Parses query to determine type (semantic, attributed, temporal)
        and extracts metadata (sender, start_date, end_date).
        """
        if reference_date is None:
            # Default reference date matching dataset time span (April 2024)
            reference_date = datetime(2024, 4, 30)

        query_lower = query.lower().strip()
        
        # Check for Attributed Search (Participant match)
        detected_sender = self.detect_sender(query)
        
        # Check for Temporal Search
        time_range = self.detect_temporal_range(query_lower, reference_date)

        query_type = "semantic"
        if detected_sender and time_range:
            query_type = "attributed"  # Attributed with temporal scope
        elif detected_sender:
            query_type = "attributed"
        elif time_range:
            query_type = "temporal"

        return {
            "query_type": query_type,
            "sender": detected_sender,
            "start_date": time_range[0] if time_range else None,
            "end_date": time_range[1] if time_range else None
        }

    def detect_sender(self, query: str) -> Optional[str]:
        query_words = re.findall(r'\b\w+\b', query)
        for word in query_words:
            for p in self.participants:
                if word.lower() == p.lower():
                    return p
        return None

    def detect_temporal_range(self, query_lower: str, ref_date: datetime) -> Optional[Tuple[datetime, datetime]]:
        # 1. "last month"
        if "last month" in query_lower:
            # Assuming ref_date is April 2024 -> last month is March 2024
            year = ref_date.year
            month = ref_date.month - 1
            if month == 0:
                month = 12
                year -= 1
            start = datetime(year, month, 1)
            # End of month
            next_m = month + 1 if month < 12 else 1
            next_y = year if month < 12 else year + 1
            end = datetime(next_y, next_m, 1) - timedelta(seconds=1)
            return (start, end)

        # 2. "this month"
        if "this month" in query_lower:
            start = datetime(ref_date.year, ref_date.month, 1)
            next_m = ref_date.month + 1 if ref_date.month < 12 else 1
            next_y = ref_date.year if ref_date.month < 12 else ref_date.year + 1
            end = datetime(next_y, next_m, 1) - timedelta(seconds=1)
            return (start, end)

        # 3. Specific Month + Year (e.g. "November 2023", "March 2024", "in March")
        for m_name, m_num in MONTH_NAMES.items():
            if re.search(rf'\b{m_name}\b', query_lower):
                # Look for year near month
                match_yr = re.search(r'\b(202[3-5])\b', query_lower)
                yr = int(match_yr.group(1)) if match_yr else (2023 if m_num >= 11 else 2024)

                # Check for "first week of [Month]"
                if "first week" in query_lower:
                    start = datetime(yr, m_num, 1)
                    end = datetime(yr, m_num, 7, 23, 59, 59)
                    return (start, end)
                
                # Check for "last week of [Month]"
                if "last week" in query_lower:
                    start = datetime(yr, m_num, 21)
                    next_m = m_num + 1 if m_num < 12 else 1
                    next_y = yr if m_num < 12 else yr + 1
                    end = datetime(next_y, next_m, 1) - timedelta(seconds=1)
                    return (start, end)

                # Check for "around March 18" or "around 18"
                match_day = re.search(rf'{m_name}\s+(\d{{1,2}})|around\s+(?:{m_name}\s+)?(\d{{1,2}})', query_lower)
                if match_day:
                    day = int(match_day.group(1) or match_day.group(2))
                    start = datetime(yr, m_num, max(1, day - 3))
                    end = datetime(yr, m_num, min(28, day + 3), 23, 59, 59)
                    return (start, end)

                # Default full month range
                start = datetime(yr, m_num, 1)
                next_m = m_num + 1 if m_num < 12 else 1
                next_y = yr if m_num < 12 else yr + 1
                end = datetime(next_y, next_m, 1) - timedelta(seconds=1)
                return (start, end)

        return None
