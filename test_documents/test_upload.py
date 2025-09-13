import requests
import os

def test_document_processing():
    # API endpoint
    url = "http://localhost:8000/upload"
    
    # Test document path - in the same directory as this script
    test_file_path = os.path.join(os.path.dirname(__file__), "incident_report.txt")
    
    if not os.path.exists(test_file_path):
        print(f"Test file not found at {test_file_path}")
        return
    
    # Prepare file for upload
    with open(test_file_path, 'rb') as f:
        files = {'file': ('incident_report.txt', f, 'text/plain')}
        
        try:
            # Send request
            response = requests.post(url, files=files)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Document processed successfully!")
                print("\nProcessing Results:")
                print("-" * 50)
                print(f"Document ID: {result['document_id']}")
                print("\nAlerts Detected:")
                for alert in result['alerts']:
                    print(f"\n🚨 Department: {alert['department']}")
                    print(f"   Severity: {alert['severity']}")
                    print(f"   Keywords: {', '.join(alert['keywords'])}")
                
                print("\nNotified Departments:")
                for dept in result['departments']:
                    print(f"\n📧 {dept['name']}")
                    print(f"   Severity: {dept['severity']}")
                    print(f"   Email: {dept['email']}")
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    test_document_processing()