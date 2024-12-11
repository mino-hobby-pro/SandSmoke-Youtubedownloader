import json
import urllib.parse
import datetime
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import time

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

max_time = 20  # 最大待機時間の設定
max_api_wait_time = 5  # APIリクエストの最大待機時間

class APItimeoutError(Exception):
    pass

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True

# APIリクエスト関数
def apirequest_video(url):
    global video_apis
    starttime = time.time()
    for api in video_apis:
        if time.time() - starttime >= max_time - 1:
            break
        try:
            res = httpx.get(api + url, timeout=max_api_wait_time)
            if res.status_code == 200 and is_json(res.text):
                print(f"動画API成功: {api}")  # 成功したAPIをログに出力
                return res.text
            else:
                print(f"エラー: {api}")
                video_apis.append(api)
                video_apis.remove(api)
        except Exception as e:
            print(f"タイムアウト: {api} - エラー: {e}")
            video_apis.append(api)
            video_apis.remove(api)
    raise APItimeoutError("動画APIがタイムアウトしました")

def getting_data(videoid):
    # 代替APIリスト
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
    try:
        # 最初にAPIからデータを取得しようとする
        t = json.loads(apirequest_video(r"api/v1/videos/" + urllib.parse.quote(videoid)))
    except (APItimeoutError, json.JSONDecodeError) as e:
        print(f"データ取得に失敗しました: {e}")
        # 失敗したときには代替の方法を使用する
        return getting_data(videoid)

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
    }

    return related_videos, video_data

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
