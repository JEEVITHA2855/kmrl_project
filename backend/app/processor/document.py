from typing import Dict
from .alert_detector import AlertDetector
import os

class DocumentProcessor:
    def __init__(self):
        self.alert_detector = AlertDetector()

    async def process_document(self, file_path: str) -> Dict:
        try:
            # Parse document content
            from .document_parser import DocumentParser
            parser = DocumentParser()
            content = parser.parse(file_path)
            if not content:
                raise ValueError("No content extracted from document")
                
            # Get accuracy metrics
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from tests.accuracy_tester import AccuracyTester
            tester = AccuracyTester()
            accuracy_results = tester.run_accuracy_test()

            # Detect alerts
            alerts = self.alert_detector.detect_alerts(content)

            # Prepare response
            result = {
                'file_name': os.path.basename(file_path),
                'content_preview': content[:200] + '...' if len(content) > 200 else content,
                'alerts': alerts,
                'metrics': accuracy_results['metrics'],
                'overall_accuracy': accuracy_results['overall_accuracy'],
                'departments': [
                    {
                        'name': alert['department'].title() + ' Department',
                        'severity': alert['severity'],
                        'keywords': alert['keywords']
                    } for alert in alerts
                ]
            }

            return result
            
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")

async def process_document(file_path: str) -> Dict:
    processor = DocumentProcessor()
    return await processor.process_document(file_path)