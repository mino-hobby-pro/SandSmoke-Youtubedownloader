import json
import urllib.parse
import datetime
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Invidious API URLs
requestAPI_urls = [
    'https://inv.nadeko.net/',
    'https://inv.zzls.xyz/',
    'https://invidious.nerdvpn.de/',
    'https://youtube.privacyplz.org/'
]

class APIError(Exception):
    def __init__(self, base_url, status_code, message):
        self.base_url = base_url
        self.status_code = status_code
        self.message = message

def requestAPI(endpoint):
    for base_url in requestAPI_urls:
        try:
            response = httpx.get(f"{base_url}{endpoint}")
            response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
            return response.text
        except httpx.HTTPStatusError as e:
            raise APIError(base_url, e.response.status_code, e.response.text)
        except Exception as e:
            raise APIError(base_url, None, str(e))
    return None

def getVideoData(videoid):
    try:
        response_text = requestAPI(f"/videos/{urllib.parse.quote(videoid)}")
    except APIError as e:
        raise HTTPException(status_code=404, detail={
            "message": "動画が見つかりませんでした。",
            "base_url": e.base_url,
            "status_code": e.status_code,
            "error_message": e.message
        })

    try:
        t = json.loads(response_text)

        # 推奨動画の取得
        recommended_videos = t.get("recommendedvideo") or t.get("recommendedVideos", [])

        # メイン動画データの準備
        video_data = {
            'video_urls': list(reversed([i["url"] for i in t.get("formatStreams", [])]))[:2],
            'description_html': t.get("descriptionHtml", "").replace("\n", "<br>"),
            'title': t.get("title", "タイトル不明"),
            'length_text': str(datetime.timedelta(seconds=t.get("lengthSeconds", 0))),
            'author_id': t.get("authorId", "不明"),
            'author': t.get("author", "不明"),
            'author_thumbnails_url': t.get("authorThumbnails", [{}])[-1].get("url", ""),
            'view_count': t.get("viewCount", "不明"),
            'like_count': t.get("likeCount", "不明"),
            'subscribers_count': t.get("subCountText", "不明")
        }

        # 推奨動画データの準備
        recommended_videos_data = [
            {
                "video_id": i.get("videoId", "不明"),
                "title": i.get("title", "タイトル不明"),
                "author_id": i.get("authorId", "不明"),
                "author": i.get("author", "不明"),
                "length_text": str(datetime.timedelta(seconds=i.get("lengthSeconds", 0))),
                "view_count_text": i.get("viewCountText", "不明")
            } for i in recommended_videos
        ]

        return video_data, recommended_videos_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail={
            "message": "JSONレスポンスのデコードに失敗しました。",
            "response": response_text
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"エラーが発生しました: {str(e)}"})

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

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
