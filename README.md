# Document Processing System

A system that processes documents, detects alerts, and routes them to appropriate departments.

## Setup Instructions

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Start the Backend Server**
```bash
cd backend
python run.py
```
The server will start at http://127.0.0.1:8000

3. **Open the Interface**
- Navigate to `test_documents/test_interface.html`
- Open it in a web browser

## Running Tests

To run accuracy tests:
```bash
cd backend
python tests/accuracy_tester.py
```

## Supported File Types
- Text files (.txt)
- PDF files (.pdf)
- Word documents (.doc, .docx)

## Features
- Document upload and processing
- Alert detection with severity levels
- Department routing
- Accuracy metrics
- Real-time processing results