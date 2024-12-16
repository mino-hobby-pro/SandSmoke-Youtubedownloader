import json
import requests
import urllib.parse
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union
import datetime

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

    # Stream URL の抽出処理
    recommended_videos = video_data.get("recommendedVideos", [])
    video_info = {
        'video_urls': list(reversed([stream["url"] for stream in video_data.get("formatStreams", [])]))[:2],
        'description_html': video_data.get("descriptionHtml", "").replace("\n", "<br>"),
        'title': video_data.get("title", "タイトルなし"),
        'length_text': str(datetime.timedelta(seconds=video_data.get("lengthSeconds", 0))),
        'author_id': video_data.get("authorId", "不明"),
        'author': video_data.get("author", "不明"),
        'author_thumbnails_url': video_data.get("authorThumbnails", [{}])[-1].get("url", ""),
        'view_count': video_data.get("viewCount", "不明"),
        'like_count': video_data.get("likeCount", "不明"),
        'subscribers_count': video_data.get("subCountText", "不明"),
    }

    return templates.TemplateResponse("video.html", {
        "request": request,
        "video": video_info,
        "recommended_videos": recommended_videos
    })
