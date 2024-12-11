import urllib.parse
import httpx
import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

# Invidious API URL
invidious_base_url = 'https://inv.nadeko.net/api/v1/videos/'

async def requestAPI(videoid):
    url = f"{invidious_base_url}{urllib.parse.quote(videoid)}"
    try:
        response = await httpx.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP status
        return response.text  # Return the response text
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

def extract_video_url(html_content):
    # Use regex to find the URL in the form of "url":"https://..."
    match = re.search(r'"url":"(https://[^"]+)"', html_content)
    if match:
        return match.group(1)  # Return the matched URL
    else:
        raise HTTPException(status_code=404, detail="Video URL not found in the response.")

@app.get("/video/{videoid}", response_class=HTMLResponse)
async def get_video(videoid: str):
    html_content = await requestAPI(videoid)
    video_url = extract_video_url(html_content)  # Extract the video URL
    return HTMLResponse(content=f"<h1>Video URL</h1><p>{video_url}</p>")

@app.get("/")
async def root():
    return {"message": "Welcome to the Video API! Use the /video/{videoid} endpoint to fetch video details."}

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
