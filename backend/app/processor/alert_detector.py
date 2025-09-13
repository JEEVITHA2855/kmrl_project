from typing import List, Dict
import re

class AlertDetector:
    def __init__(self):
        self.alert_patterns = {
            'safety': r'(?i)(hazard|danger|emergency|evacuation|safety concern|chemical|fire)',
            'maintenance': r'(?i)(maintenance|repair|breakdown|malfunction|delay|equipment)',
            'hr': r'(?i)(personnel|employee|staff|workforce|attendance|injury)'
        }
        
    def detect_alerts(self, text: str) -> List[Dict]:
        alerts = []
        
        for dept, pattern in self.alert_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                alerts.append({
                    'department': dept,
                    'keywords': list(set(matches)),
                    'severity': self._calculate_severity(text)
                })
        
        return alerts

    def _calculate_severity(self, text: str) -> str:
        urgent_words = ['immediate', 'urgent', 'emergency', 'critical']
        warning_words = ['caution', 'warning', 'attention']
        
        urgent_count = sum(1 for word in urgent_words if word.lower() in text.lower())
        warning_count = sum(1 for word in warning_words if word.lower() in text.lower())
        
        if urgent_count >= 2:
            return 'critical'
        elif urgent_count == 1 or warning_count >= 2:
            return 'high'
        elif warning_count == 1:
            return 'medium'
        return 'low'