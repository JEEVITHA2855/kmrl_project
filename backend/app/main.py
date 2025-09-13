from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiofiles
import os
import magic
import logging
from datetime import datetime
import json

from .processor.document import process_document
from .utils.email_sender import send_alert_emails

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Processing System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_MIME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
]

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "data", "document_history.json")

def save_to_history(document_data: dict):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    # Read existing history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = {"documents": []}
    
    # Add timestamp and document data
    document_data['timestamp'] = datetime.now().isoformat()
    history['documents'].append(document_data)
    
    # Save updated history
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@app.get("/")
async def root():
    return {"status": "running", "service": "Document Processing API"}

@app.get("/documents/")
async def get_documents():
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        
        if not os.path.exists(HISTORY_FILE):
            # Initialize empty history file
            with open(HISTORY_FILE, 'w') as f:
                json.dump({"documents": []}, f)
            return {"documents": []}
            
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        # Sort documents by severity and timestamp
        documents = history.get('documents', [])
        if not isinstance(documents, list):
            documents = []
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        documents.sort(
            key=lambda x: (severity_order.get(x.get('highest_severity', 'low'), 4), x.get('timestamp', '')),
            reverse=True
        )
        
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file existence
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(upload_dir, file.filename)
        logger.info(f"Saving file to: {file_path}")
        
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")

        # Check file type
        try:
            mime_type = magic.from_file(file_path, mime=True)
            logger.info(f"Detected MIME type: {mime_type}")
            
            if mime_type not in ALLOWED_MIME_TYPES:
                os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {mime_type} not allowed. Allowed types: {ALLOWED_MIME_TYPES}"
                )
        except Exception as e:
            logger.error(f"Failed to check file type: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to validate file type")

        # Process document
        result = await process_document(file_path)
        
        # Add metadata
        result['file_name'] = file.filename
        result['highest_severity'] = max(
            (alert['severity'] for alert in result.get('alerts', [])),
            default='low',
            key=lambda x: {'critical': 3, 'high': 2, 'medium': 1, 'low': 0}[x]
        )
        
        # Save to history
        save_to_history(result)

        # Send email alerts
        if result.get('alerts'):
            try:
                await send_alert_emails(result)
            except Exception as e:
                logger.error(f"Failed to send email alerts: {str(e)}")
                # Don't raise exception here, continue with response

        return JSONResponse(content=result)

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        # Cleanup: remove the uploaded file
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Failed to cleanup file: {str(e)}")

@app.get("/test-accuracy")
async def test_accuracy():
    try:
        from tests.accuracy_tester import AccuracyTester
        tester = AccuracyTester()
        results = tester.run_accuracy_test()
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))