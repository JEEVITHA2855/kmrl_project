from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve all files in e:\kmrl_project as static files at the root URL
app.mount("/", StaticFiles(directory="e:/kmrl_project", html=True), name="static")