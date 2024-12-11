import urllib.parse
import httpx
import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

# Invidious API URL
invidious_base_url = 'https://script.google.com/macros/s/AKfycbxYjOWULjin5kpp-NcjjjGujVX3wy1TEJVUR2AZtR6-5c_q7GBr1Nctl2_Kat4lSboD/exec?videoId='

async def requestAPI(videoid):
    url = f"{invidious_base_url}{urllib.parse.quote(videoid)}"
    try:
        response = await httpx.get(url)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
        return response.text  # レスポンスを返す
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)  # エラーメッセージを返す
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラーが発生しました: {e}")  # エラーメッセージを返す

# URLを抽出する関数
def extract_url(html_content):
    # 正規表現を使って "url": "https://rr..." の形式を抽出
    match = re.search(r'"url":\s*"([^"]+)"', html_content)
    if match:
        return match.group(1)  # 最初のキャプチャグループを返す
    return None  # 見つからなかった場合は None を返す

@app.get("/video/{videoid}", response_class=HTMLResponse)
async def get_video(videoid: str):
    html_content = await requestAPI(videoid)
    extracted_url = extract_url(html_content)

    if extracted_url:
        return HTMLResponse(content=f"<h1>Video URL:</h1><p>{extracted_url}</p>")
    else:
        raise HTTPException(status_code=404, detail="URLが見つかりませんでした。")  # URLが見つからない場合はエラーを返す

@app.get("/")
async def root():
    return {"message": "Welcome to the Video API! Use the /video/{videoid} endpoint to fetch video details."}

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
