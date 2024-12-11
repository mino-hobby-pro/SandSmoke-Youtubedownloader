import urllib.parse
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

# Invidious API URL
invidious_base_url = 'https://inv.nadeko.net/api/v1/videos/'

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

@app.get("/video/{videoid}", response_class=HTMLResponse)
async def get_video(videoid: str):
    html_content = await requestAPI(videoid)
    return HTMLResponse(content=html_content)

@app.get("/")
async def root():
    return {"message": "Welcome to the Video API! Use the /video/{videoid} endpoint to fetch video details."}

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
