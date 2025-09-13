from typing import Dict
import asyncio

department_emails = {
    'Safety Department': 'safety@company.com',
    'Maintenance Department': 'maintenance@company.com',
    'Hr Department': 'hr@company.com'
}

async def send_alert_emails(result: Dict):
    for dept in result['departments']:
        dept_name = dept['name']
        dept_email = department_emails.get(dept_name, '')
        
        print(f"\n=== Alert Notification ===")
        print(f"To: {dept_name} ({dept_email})")
        print(f"Severity: {dept['severity'].upper()}")
        print(f"Keywords: {', '.join(dept['keywords'])}")
        print("=" * 25)