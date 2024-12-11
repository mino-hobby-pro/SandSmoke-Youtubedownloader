import json
import urllib.parse
import datetime
import httpx
from fastapi import FastAPI

app = FastAPI()

# Invidious API URLs
requestAPI_urls = [
    'https://inv.nadeko.net/',
    'https://inv.zzls.xyz/',
    'https://invidious.nerdvpn.de/',
    'https://youtube.privacyplz.org/'
]

def requestAPI(endpoint):
    for base_url in requestAPI_urls:
        response = httpx.get(f"{base_url}{endpoint}")
        if response.status_code == 200:
            return response.text
    return None

def getVideoData(videoid):
    t = json.loads(requestAPI(f"/videos/{urllib.parse.quote(videoid)}"))

    if 'recommendedvideo' in t:
        recommended_videos = t["recommendedvideo"]
    elif 'recommendedVideos' in t:
        recommended_videos = t["recommendedVideos"]
    else:
        recommended_videos = [{
            "videoId": "failed",
            "title": "failed",
            "authorId": "failed",
            "author": "failed",
            "lengthSeconds": 0,
            "viewCountText": "Load Failed"
        }]
    
    # Prepare the main video data
    video_data = {
        'video_urls': list(reversed([i["url"] for i in t["formatStreams"]]))[:2],
        'description_html': t["descriptionHtml"].replace("\n", "<br>"),
        'title': t["title"],
        'length_text': str(datetime.timedelta(seconds=t["lengthSeconds"])),
        'author_id': t["authorId"],
        'author': t["author"],
        'author_thumbnails_url': t["authorThumbnails"][-1]["url"],
        'view_count': t["viewCount"],
        'like_count': t["likeCount"],
        'subscribers_count': t["subCountText"]
    }

    # Prepare recommended videos data
    recommended_videos_data = [
        {
            "video_id": i["videoId"],
            "title": i["title"],
            "author_id": i["authorId"],
            "author": i["author"],
            "length_text": str(datetime.timedelta(seconds=i["lengthSeconds"])),
            "view_count_text": i["viewCountText"]
        } for i in recommended_videos
    ]
    
    return video_data, recommended_videos_data

@app.get("/video/{videoid}")
async def get_video(videoid: str):
    video_data, recommended_videos_data = getVideoData(videoid)
    
    return {
        "video_data": video_data,
        "recommended_videos": recommended_videos_data
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the Video API! Use the /video/{videoid} endpoint to fetch video details."}

# uvicornを使ってアプリを実行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
