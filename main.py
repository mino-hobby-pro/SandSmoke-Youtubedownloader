from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pytube import YouTube
import uvicorn

app = FastAPI()

@app.get("/video")
async def get_video_stream(video_id: str):
    try:
        # YouTubeオブジェクトを作成
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        # ストリームを取得
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        # ストリームURLを取得
        stream_url = stream.url if stream else None
        
        if stream_url:
            return {"stream_url": stream_url}
        else:
            raise HTTPException(status_code=404, detail="Video stream not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>SandTube API</title>
        </head>
        <body>
            <h1>Welcome to SandTube API</h1>
            <p>Use the endpoint /video?video_id=<your_video_id> to get the stream URL.</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    # uvicornを使ってアプリを実行
    uvicorn.run(app, host="0.0.0.0", port=8000)
