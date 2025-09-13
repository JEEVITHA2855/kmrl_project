import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = BASE_DIR  # or set to another directory if needed

UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_files")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

DOCUMENTS_API_PATH = "/documents/"
UPLOAD_API_PATH = "/upload/"

# Frontend URLs
UPLOAD_PAGE_URL = "/test_interface.html"
DOCUMENT_HISTORY_URL = "/test_documents/document_history.html"