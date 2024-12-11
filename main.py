import json
import urllib.parse
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

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
            return response.text, base_url  # レスポンスとAPIのURLを返す
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTPエラーが発生しました: {base_url} - ステータスコード: {e.response.status_code} - メッセージ: {e.response.text}"
            return None, error_msg  # エラーメッセージを返す
        except Exception as e:
            error_msg = f"エラーが発生しました: {e} - ベースURL: {base_url}"
            return None, error_msg  # エラーメッセージを返す
    return None, "すべてのAPIで失敗しました。"  # すべてのAPIで失敗

def getting_data(videoid):
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
                t = response.json()
                
                # 推奨動画リストの構築
                related_videos = [{
                    "id": t["videoId"],
                    "title": t["videoTitle"],
                    "authorId": t["channelId"],
                    "author": t["channelName"],
                    "viewCount": t["videoViews"]
                }]
                
                # 必要な情報を取得
                stream_urls = [
                    t["stream_url"],
                    t.get("highstreamUrl", ""),
                    t.get("audioUrl", "")
                ]
                description = t["videoDes"].replace("\n", "<br>")
                title = t["videoTitle"]
                authorId = t["channelId"]
                author = t["channelName"]
                author_icon = t["channelImage"]
                view_count = t["videoViews"]
                
                # get_dataの形式に合わせて返す
                video_data = {
                    'video_urls': stream_urls,  # ストリームURL
                    'description_html': description,
                    'title': title,
                    'author_id': authorId,
                    'author': author,
                    'author_thumbnails_url': author_icon,
                    'view_count': view_count,
                    'request_duration': None  # durationが無い場合はNone
                }

                return related_videos, video_data
        except Exception as e:
            print(f"{url} からのデータ取得に失敗しました: {e}")
    
    raise Exception("全ての代替URLからデータを取得できませんでした。")

def get_data(videoid):
    # 直接 getting_data を呼び出す
    return getting_data(videoid)

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
