import json
import urllib.parse
import datetime
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import time

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
        start_time = time.time()  # リクエスト開始時間
        try:
            response = httpx.get(f"{base_url}{endpoint}")
            response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
            duration = time.time() - start_time  # リクエストにかかった時間
            return response.text, base_url, duration  # レスポンスとAPIのURL、かかった時間を返す
        except httpx.HTTPStatusError as e:
            duration = time.time() - start_time
            error_msg = f"HTTPエラーが発生しました: {base_url} - ステータスコード: {e.response.status_code} - メッセージ: {e.response.text} - 時間: {duration:.2f}秒"
            return None, error_msg, duration  # エラーメッセージを返す
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"エラーが発生しました: {e} - ベースURL: {base_url} - 時間: {duration:.2f}秒"
            return None, error_msg, duration  # エラーメッセージを返す
    return None, "すべてのAPIで失敗しました。", None  # すべてのAPIで失敗

def get_data(videoid):
    response_text, error_msg, duration = requestAPI(f"/videos/{urllib.parse.quote(videoid)}")
    
    if response_text is None:
        raise HTTPException(status_code=404, detail=error_msg)

    try:
        t = json.loads(response_text)

        # 関連動画を解析してリストにする
        related_videos = [
            {
                "id": i["videoId"],
                "title": i["title"],
                "authorId": i["authorId"],
                "author": i["author"],
                "viewCount": i["viewCount"]
            }
            for i in t.get("recommendedVideos", [])
        ]

        # メイン動画データの準備
        video_data = {
            'video_urls': list(reversed([i["url"] for i in t.get("formatStreams", [])]))[:2],
            'description_html': t.get("descriptionHtml", "").replace("\n", "<br>"),
            'title': t.get("title", "タイトル不明"),
            'author_id': t.get("authorId", "不明"),
            'author': t.get("author", "不明"),
            'author_thumbnails_url': t.get("authorThumbnails", [{}])[-1].get("url", ""),
            'view_count': t.get("viewCount", "不明"),
            'request_duration': duration,  # リクエストにかかった時間
        }

        return related_videos, video_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="JSONレスポンスのデコードに失敗しました。サーバーの応答: " + response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラーが発生しました: {str(e)}")

@app.get("/video/{videoid}", response_class=HTMLResponse)
async def get_video(videoid: str):
    related_videos, video_data = get_data(videoid)
    
    # HTML形式での応答
    html_content = f"""
    <h1>動画データ</h1>
    <pre>{json.dumps(video_data, ensure_ascii=False, indent=4)}</pre>
    <h1>関連動画</h1>
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
