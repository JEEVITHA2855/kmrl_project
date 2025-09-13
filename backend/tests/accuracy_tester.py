import json
from typing import Dict, List
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.processor.alert_detector import AlertDetector
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

class AccuracyTester:
    def __init__(self):
        self.alert_detector = AlertDetector()
        
    def load_test_cases(self, test_file: str) -> List[Dict]:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_path = os.path.join(base_path, 'test_documents', 'test_cases.json')
        with open(full_path, 'r') as f:
            data = json.load(f)
            return data.get('test_cases', [])

    def evaluate_single_case(self, test_case: Dict) -> Dict:
        # Get system prediction
        alerts = self.alert_detector.detect_alerts(test_case['document'])
        
        # Extract predictions
        predicted_depts = set([alert['department'] for alert in alerts])
        predicted_severity = max([alert['severity'] for alert in alerts], default='low')
        predicted_keywords = set([kw.lower() for alert in alerts for kw in alert['keywords']])
        
        # Extract expected values
        expected_depts = set(test_case['expected']['departments'])
        expected_severity = test_case['expected']['severity']
        expected_keywords = set([kw.lower() for kw in test_case['expected']['keywords']])
        
        # Calculate accuracy metrics
        dept_accuracy = len(predicted_depts.intersection(expected_depts)) / len(expected_depts) if expected_depts else 1.0
        severity_accuracy = 1.0 if predicted_severity == expected_severity else 0.0
        keyword_accuracy = len(predicted_keywords.intersection(expected_keywords)) / len(expected_keywords) if expected_keywords else 1.0
        
        return {
            'department_accuracy': dept_accuracy,
            'severity_accuracy': severity_accuracy,
            'keyword_accuracy': keyword_accuracy,
            'predicted': {
                'departments': list(predicted_depts),
                'severity': predicted_severity,
                'keywords': list(predicted_keywords)
            },
            'expected': test_case['expected']
        }

    def run_accuracy_test(self, test_file: str = 'test_documents/test_cases.json') -> Dict:
        test_cases = self.load_test_cases(test_file)
        results = []
        
        for case in test_cases:
            result = self.evaluate_single_case(case)
            results.append(result)
        
        # Calculate overall metrics
        avg_dept_accuracy = sum(r['department_accuracy'] for r in results) / len(results)
        avg_severity_accuracy = sum(r['severity_accuracy'] for r in results) / len(results)
        avg_keyword_accuracy = sum(r['keyword_accuracy'] for r in results) / len(results)
        
        overall_accuracy = (avg_dept_accuracy + avg_severity_accuracy + avg_keyword_accuracy) / 3
        
        # Generate detailed report
        report = {
            'overall_accuracy': overall_accuracy,
            'metrics': {
                'department_accuracy': avg_dept_accuracy,
                'severity_accuracy': avg_severity_accuracy,
                'keyword_accuracy': avg_keyword_accuracy
            },
            'detailed_results': results
        }
        
        # Save visualizations
        self._generate_visualizations(results)
        
        return report

    def _generate_visualizations(self, results: List[Dict]):
        # Create accuracy comparison chart
        metrics = ['Department', 'Severity', 'Keyword']
        values = [
            sum(r['department_accuracy'] for r in results) / len(results),
            sum(r['severity_accuracy'] for r in results) / len(results),
            sum(r['keyword_accuracy'] for r in results) / len(results)
        ]
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=metrics, y=values)
        plt.title('Accuracy by Component')
        plt.ylabel('Accuracy Score')
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        plt.savefig(os.path.join(base_path, 'test_documents', 'accuracy_metrics.png'))
        plt.close()

if __name__ == "__main__":
    tester = AccuracyTester()
    results = tester.run_accuracy_test()
    print("\n=== Accuracy Test Results ===")
    print(f"Overall Accuracy: {results['overall_accuracy']:.2%}")
    print("\nComponent Accuracies:")
    for metric, value in results['metrics'].items():
        print(f"{metric}: {value:.2%}")
    print("\nVisualization saved as 'accuracy_metrics.png'")