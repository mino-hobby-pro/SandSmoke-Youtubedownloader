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
            print(f"HTTPエラーが発生しました: {base_url} - ステータスコード: {e.response.status_code} - メッセージ: {e.response.text} - 時間: {duration:.2f}秒")
        except Exception as e:
            duration = time.time() - start_time
            print(f"エラーが発生しました: {e} - ベースURL: {base_url} - 時間: {duration:.2f}秒")
    return None, None, None  # すべてのAPIで失敗

def getVideoData(videoid):
    response_text, base_url, duration = requestAPI(f"/videos/{urllib.parse.quote(videoid)}")
    
    if response_text is None:
        raise HTTPException(status_code=404, detail="動画が見つかりませんでした。全てのAPIに対してリクエストに失敗しました。")

    try:
        t = json.loads(response_text)

        # 推奨動画の取得
        recommended_videos = t.get("recommendedvideo", t.get("recommendedVideos", []))

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
            'subscribers_count': t.get("subCountText", "不明"),
            'request_duration': duration,  # リクエストにかかった時間
            'base_url': base_url  # 成功したAPIのURL
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

@app.get("/video/{videoid}", response_class=HTMLResponse)
async def get_video(videoid: str):
    video_data, recommended_videos_data = getVideoData(videoid)
    
    # HTML形式での応答
    html_content = f"""
    <h1>動画データ</h1>
    <pre>{json.dumps(video_data, ensure_ascii=False, indent=4)}</pre>
    <h1>推奨動画</h1>
    <pre>{json.dumps(recommended_videos_data, ensure_ascii=False, indent=4)}</pre>
    """
    return HTMLResponse(content=html_content)

@app.get("/")
async def root():
    return {"message": "Welcome to the Video API! Use the /video/{videoid} endpoint to fetch video details."}

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
