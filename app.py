import json
import requests
import urllib.parse
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory='templates')

# 動画情報を取得するためのAPI
API_URL = "https://invidious.snopyta.org/api/v1"

def get_search_results(query):
    response = requests.get(f"{API_URL}/search?q={urllib.parse.quote(query)}")
    return response.json()

def get_video_data(video_id):
    response = requests.get(f"{API_URL}/videos/{video_id}")
    return response.json()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str):
    results = get_search_results(q)
    return templates.TemplateResponse("search.html", {"request": request, "results": results})

@app.get("/watch/{video_id}", response_class=HTMLResponse)
def watch(request: Request, video_id: str):
    video_data = get_video_data(video_id)
    return templates.TemplateResponse("video.html", {"request": request, "video": video_data})

