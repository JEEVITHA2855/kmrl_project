import uvicorn
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the FastAPI server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Using localhost instead of 0.0.0.0
        port=8000,
        reload=True
    )