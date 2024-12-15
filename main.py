from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import threading

app = Flask(__name__)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_id = request.form['video_id']
    if not os.path.exists('videos'):
        os.makedirs('videos')
    
    thread = threading.Thread(target=download_video, args=(video_id,))
    thread.start()
    
    return jsonify({"status": "ダウンロードを開始しました。"})

@app.route('/status', methods=['GET'])  # GETメソッドを明示的に指定
def status():
    return jsonify(download_status)

if __name__ == "__main__":
    app.run(debug=True)
