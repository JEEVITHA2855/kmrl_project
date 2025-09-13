from opensearchpy import OpenSearch
from datetime import datetime
from typing import Dict, Any, List
import os

class OpenSearchClient:
    def __init__(self):
        self.client = OpenSearch(
            hosts=[{
                'host': os.getenv('OPENSEARCH_HOST', 'opensearch'),
                'port': int(os.getenv('OPENSEARCH_PORT', 9200))
            }],
            http_auth=None,
            use_ssl=False
        )
        self.document_index = 'documents'
        self.alerts_index = 'alerts'
        self._setup_indices()

    def _setup_indices(self):
        document_mapping = {
            "mappings": {
                "properties": {
                    "content": {"type": "text"},
                    "summary": {"type": "text"},
                    "tags": {"type": "keyword"},
                    "translations": {"type": "object"},
                    "created_at": {"type": "date"},
                    "file_name": {"type": "keyword"}
                }
            }
        }

        alerts_mapping = {
            "mappings": {
                "properties": {
                    "document_id": {"type": "keyword"},
                    "department": {"type": "keyword"},
                    "severity": {"type": "keyword"},
                    "keywords": {"type": "keyword"},
                    "created_at": {"type": "date"}
                }
            }
        }

        for index, mapping in [(self.document_index, document_mapping), 
                             (self.alerts_index, alerts_mapping)]:
            if not self.client.indices.exists(index=index):
                self.client.indices.create(index=index, body=mapping)

    async def store_document(self, doc_data: Dict[str, Any]) -> str:
        doc_data['created_at'] = datetime.utcnow()
        response = self.client.index(
            index=self.document_index,
            body=doc_data
        )
        return response['_id']

    async def store_alerts(self, doc_id: str, alerts: List[Dict]) -> None:
        for alert in alerts:
            alert_data = {
                'document_id': doc_id,
                'department': alert['department'],
                'severity': alert['severity'],
                'keywords': alert['keywords'],
                'created_at': datetime.utcnow()
            }
            self.client.index(
                index=self.alerts_index,
                body=alert_data
            )

    async def get_document(self, doc_id: str) -> Dict:
        response = self.client.get(
            index=self.document_index,
            id=doc_id
        )
        return response['_source']