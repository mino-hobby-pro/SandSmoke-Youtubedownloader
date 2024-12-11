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

def requestAPI(endpoint):
    for base_url in requestAPI_urls:
        try:
            response = httpx.get(f"{base_url}{endpoint}")
            response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
            return response.text
        except httpx.HTTPStatusError as e:
            print(f"HTTPエラーが発生しました: {base_url} - ステータスコード: {e.response.status_code} - メッセージ: {e.response.text}")
        except Exception as e:
            print(f"エラーが発生しました: {e} - ベースURL: {base_url}")
    return None


def getVideoData(videoid):
    response_text = requestAPI(f"/videos/{urllib.parse.quote(videoid)}")
    
    if response_text is None:
        raise HTTPException(status_code=404, detail="動画が見つかりませんでした。全てのAPIに対してリクエストに失敗しました。")

    try:
        t = json.loads(response_text)

        # 推奨動画の取得
        if 'recommendedvideo' in t:
            recommended_videos = t["recommendedvideo"]
        elif 'recommendedVideos' in t:
            recommended_videos = t["recommendedVideos"]
        else:
            recommended_videos = []

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
        raise HTTPException(status_code=500, detail="JSONレスポンスのデコードに失敗しました。サーバーの応答: " + response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラーが発生しました: {str(e)}")


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
