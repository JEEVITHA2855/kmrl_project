# alert_engine.py
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
import time
from datetime import datetime

OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
ADMIN_USER = "admin"
ADMIN_PASS = "ChangeMeAdmin123!"

INDEX_NAME = "summarized_documents"
ALERT_KEYWORDS = ["risk", "hazard", "danger", "urgent", "shutdown", "delayed", "threaten", "incident"]
DEPARTMENTS_FILE = "departments.json"
OUTPUT_ALERT_FOLDER = "outgoing_alerts"  # simulates sending alerts (store JSONs here)

# Connect client
client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    http_auth=(ADMIN_USER, ADMIN_PASS),
    use_ssl=False,
    verify_certs=False,
    connection_class=RequestsHttpConnection,
)

# Load departments
with open(DEPARTMENTS_FILE, "r", encoding="utf-8") as f:
    departments = json.load(f)

# Ensure output folder exists
import os
os.makedirs(OUTPUT_ALERT_FOLDER, exist_ok=True)

def find_alerts():
    # Search for docs containing alert keywords in the summary.
    # We'll do a simple match query with OR on keywords.
    query_string = " OR ".join(ALERT_KEYWORDS)
    body = {
        "query": {
            "simple_query_string": {
                "query": query_string,
                "fields": ["summary"],
                "default_operator": "and"
            }
        }
    }
    res = client.search(index=INDEX_NAME, body=body, size=100)
    hits = res.get("hits", {}).get("hits", [])
    return [h["_source"] for h in hits]

def route_alert(doc):
    tag = doc.get("tag")
    routed_to = departments.get(tag, [])
    alert_payload = {
        "doc_id": doc.get("doc_id"),
        "tag": tag,
        "summary": doc.get("summary"),
        "translation": doc.get("translation"),
        "timestamp": doc.get("timestamp"),
        "routed_to": routed_to,
        "detected_at": datetime.utcnow().isoformat() + "Z"
    }
    # Simulate sending by writing JSON to outgoing_alerts folder
    out_file = os.path.join(OUTPUT_ALERT_FOLDER, f"alert_{doc.get('doc_id')}_{int(time.time())}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(alert_payload, f, ensure_ascii=False, indent=2)
    print(f"Alert routed for {doc.get('doc_id')} -> {routed_to} (written {out_file})")

def run_once():
    hits = find_alerts()
    if not hits:
        print("No alerts found.")
        return
    for doc in hits:
        route_alert(doc)

if __name__ == "__main__":
    # For demo, run once. In prod, schedule or run as worker.
    run_once()
