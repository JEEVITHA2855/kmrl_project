from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Department:
    id: str
    name: str
    email: str
    keywords: List[str]

class DepartmentService:
    def __init__(self):
        self.departments = {
            'safety': Department(
                id='safety',
                name='Safety Department',
                email='safety@company.com',
                keywords=['fire', 'hazard', 'chemical', 'emergency']
            ),
            'maintenance': Department(
                id='maintenance',
                name='Maintenance Department',
                email='maintenance@company.com',
                keywords=['repair', 'breakdown', 'delay']
            ),
            'hr': Department(
                id='hr',
                name='Human Resources',
                email='hr@company.com',
                keywords=['employee', 'personnel', 'staff']
            )
        }

    def get_relevant_departments(self, alerts: List[Dict]) -> List[Department]:
        relevant_depts = []
        for alert in alerts:
            if dept := self.departments.get(alert['department']):
                relevant_depts.append(dept)
        return list(set(relevant_depts))