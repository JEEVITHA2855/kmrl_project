from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.abspath(os.path.dirname(__file__))
DOCUMENTS_JSON = os.path.join(STATIC_DIR, "documents.json")

# Create required directories
from settings import UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files first, but not at root
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


async def scan_for_alerts(content: bytes, filename: str):
    """
    Simplified scan function that only returns severity level, departments, and keywords.
    No detailed alerts list.
    """
    alert_patterns = {
        "critical": ["urgent", "emergency", "critical", "immediate action", "severe", "risk", "danger", "shutdown", "hazard", "delayed"],
        "high": ["important", "priority", "alert", "warning", "security"],
        "medium": ["attention", "review", "check", "notify", "consider"],
        "low": ["info", "update", "status", "report", "normal"]
    }

    text = content.decode("utf-8", errors="ignore").lower()
    highest_severity = "low"
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    found_keywords = []

    for severity, keywords in alert_patterns.items():
        for keyword in keywords:
            if keyword in text:
                found_keywords.append(keyword)
                if severity_order[severity] < severity_order[highest_severity]:
                    highest_severity = severity

    # Determine departments
    departments = []
    dept_keywords = {
        "HR": ["employee", "personnel", "hiring", "staff"],
        "Finance": ["budget", "cost", "payment", "financial"],
        "IT": ["system", "network", "software", "technical"],
        "Admin": ["facility", "office", "administrative", "management"]
    }

    for dept, keywords in dept_keywords.items():
        if any(keyword in text for keyword in keywords):
            departments.append(dept)

    return {
        "highest_severity": highest_severity if found_keywords else "low",
        "departments": departments or ["General"],
        "keywords": list(set(found_keywords))
    }


# API endpoints
@app.post("/api/upload")
async def upload_files(files: list[UploadFile]):
    try:
        processed_docs = []
        for file in files:
            content = await file.read()
            file_location = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_location, "wb") as f:
                f.write(content)

            scan_results = await scan_for_alerts(content, file.filename)
            
            doc_info = {
                "file_name": file.filename,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "highest_severity": scan_results["highest_severity"],
                "departments": scan_results["departments"],
                "keywords": scan_results["keywords"]
            }
            processed_docs.append(doc_info)

        all_docs = {"documents": []}
        if os.path.exists(DOCUMENTS_JSON):
            with open(DOCUMENTS_JSON, "r", encoding="utf-8") as f:
                all_docs = json.load(f)
        all_docs["documents"].extend(processed_docs)
        with open(DOCUMENTS_JSON, "w", encoding="utf-8") as f:
            json.dump(all_docs, f, ensure_ascii=False, indent=2)

        return JSONResponse({
            "status": "success",
            "processed": processed_docs,
            "message": f"Processed {len(processed_docs)} files"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


def get_severity_order(severity: str) -> int:
    order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
        "none": 4
    }
    return order.get(severity.lower(), 5)


@app.get("/api/documents")
async def get_documents():
    try:
        if os.path.exists(DOCUMENTS_JSON):
            with open(DOCUMENTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["documents"].sort(
                    key=lambda x: get_severity_order(x.get("highest_severity", "none"))
                )
                return data
        return {"documents": []}
    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.get("/{full_path:path}")
async def serve_static(full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse({"detail": "Not found"}, status_code=404)

    if full_path in ["", "/"]:
        full_path = "test_interface.html"

    file_path = os.path.join(STATIC_DIR, full_path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(STATIC_DIR, "test_interface.html"))
