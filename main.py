from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import threading

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

download_status = {"status": "待機中", "current_step": ""}

def download_video(video_id):
    global download_status
    download_status["status"] = "ダウンロード中..."
    download_status["current_step"] = "動画のダウンロードを開始します。"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'videos/{video_id}.%(ext)s',
        'progress_hooks': [hook],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
    
    download_status["status"] = "ダウンロード完了！"
    download_status["current_step"] = "動画の読み込み中..."

def hook(d):
    if d['status'] == 'downloading':
        download_status["current_step"] = f"残り: {d['downloaded_bytes'] / d['total_bytes']:.2%} 完了"

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/download")
async def download(video_id: str = Form(...)):
    if not os.path.exists('videos'):
        os.makedirs('videos')
    
    thread = threading.Thread(target=download_video, args=(video_id,))
    thread.start()
    
    return JSONResponse(content={"status": "ダウンロードを開始しました。"})

@app.get("/status")
async def status():
    return JSONResponse(content=download_status)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
