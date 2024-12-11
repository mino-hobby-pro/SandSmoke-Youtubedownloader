import json
import urllib.parse
import time
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

# Invidious API URLs
video_apis = [
    r"https://invidious.jing.rocks/",
    r"https://invidious.nerdvpn.de/",
    r"https://script.google.com/macros/s/AKfycbxic9NV_JbKs1Ia4m5yw6z7nAZjkQ0mjZ2FGi29ZtLMhX9R6JSEO6jZBuXpNyWHCuRy/exec?videoId=",
    r"https://script.google.com/macros/s/AKfycbzDTu2EJQrGPPU-YS3EFarXbfh9zGB1zR9ky-9AunHl7Yp3Gq83rh1726JYjxbjbEsB/exec?videoId=",
    r"https://script.google.com/macros/s/AKfycbw43HTKJe0khOM3h5lrRbWw2OUONcbQCsnSry7F6c_1bPdtxVjTUotm1_XY2KfqMLWT/exec?videoId=",
    r"https://script.google.com/macros/s/AKfycbxYjOWULjin5kpp-NcjjjGujVX3wy1TEJVUR2AZtR6-5c_q7GBr1Nctl2_Kat4lSboD/exec?videoId=",
]

max_time = 20  # Maximum wait time for API requests
max_api_wait_time = 5  # Maximum wait time for individual API requests

class APItimeoutError(Exception):
    pass

def is_json(response_text):
    try:
        json.loads(response_text)
        return True
    except ValueError:
        return False

async def fetch_video_data(api, videoid):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api + urllib.parse.quote(videoid), timeout=max_api_wait_time)
            if response.status_code == 200 and is_json(response.text):
                return response.json()
        except Exception as e:
            print(f"Error fetching from {api}: {e}")
    return None

async def apirequest_video(videoid):
    tasks = [fetch_video_data(api, videoid) for api in video_apis]
    responses = await httpx.gather(*tasks)

    # Return the first successful response
    for response in responses:
        if response:
            return response
    raise APItimeoutError("All video APIs timed out.")

def getting_data(videoid):
    # Alternative API list
    urls = [
        f"https://ludicrous-wonderful-temple.glitch.me/api/login/{urllib.parse.quote(videoid)}",
        f"https://free-sudden-kiss.glitch.me/api/login/{urllib.parse.quote(videoid)}",
        f"https://wakame02m.glitch.me/api/login/{urllib.parse.quote(videoid)}",
        f"https://natural-voltaic-titanium.glitch.me/api/login/{urllib.parse.quote(videoid)}",
        f"https://watawatawata.glitch.me/api/{urllib.parse.quote(videoid)}?token=wakameoishi",
        f"https://jade-highfalutin-account.glitch.me/api/login/{urllib.parse.quote(videoid)}"
    ]
    
    for url in urls:
        try:
            response = httpx.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Failed to fetch data from {url}: {e}")

    raise Exception("Data could not be retrieved from all alternative URLs.")

async def get_data(videoid):
    try:
        # Attempt to fetch data from the primary APIs
        video_data = await apirequest_video(f"api/v1/videos/{videoid}")
    except (APItimeoutError, json.JSONDecodeError) as e:
        print(f"Failed to fetch data: {e}")
        return getting_data(videoid)

    # Parse related videos from the response
    related_videos = [
        {
            "id": i["videoId"],
            "title": i["title"],
            "authorId": i["authorId"],
            "author": i["author"],
            "viewCount": i["viewCount"]
        }
        for i in video_data.get("recommendedVideos", [])
    ]

    # Prepare the main video data
    video_details = {
        'video_urls': [i["url"] for i in video_data.get("formatStreams", [])],
        'description_html': video_data.get("descriptionHtml", "").replace("\n", "<br>"),
        'title': video_data.get("title", "Unknown Title"),
        'author_id': video_data.get("authorId", "Unknown"),
        'author': video_data.get("author", "Unknown"),
        'author_thumbnails_url': video_data.get("authorThumbnails", [{}])[-1].get("url", ""),
        'view_count': video_data.get("viewCount", "Unknown"),
    }

    return related_videos, video_details

@app.get("/video/{videoid}", response_class=HTMLResponse)
async def get_video(videoid: str):
    related_videos, video_details = await get_data(videoid)
    
    # Construct HTML response
    html_content = f"""
    <h1>Video Data</h1>
    <pre>{json.dumps(video_details, ensure_ascii=False, indent=4)}</pre>
    <h1>Related Videos</h1>
    <pre>{json.dumps(related_videos, ensure_ascii=False, indent=4)}</pre>
    """
    return HTMLResponse(content=html_content)

@app.get("/")
async def root():
    return {"message": "Welcome to the Video API! Use the /video/{videoid} endpoint to fetch video details."}

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
