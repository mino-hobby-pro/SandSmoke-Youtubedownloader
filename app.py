import json
import requests
import urllib.parse
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# APIの基礎URL
API_BASE_URL = "https://inv.nadeko.net/api/v1" 

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
def search(q: str, request: Request, page: int = 1):
    response = requests.get(f"{API_BASE_URL}/search?q={urllib.parse.quote(q)}&page={page}")
    results = response.json()
    return templates.TemplateResponse("search.html", {"request": request, "results": results, "query": q})

@app.get("/watch/{video_id}", response_class=HTMLResponse)
def watch(video_id: str, request: Request):
    response = requests.get(f"{API_BASE_URL}/videos/{video_id}")
    video_data = response.json()
    return templates.TemplateResponse("video.html", {
        "request": request,
        "video": video_data
    })


