from flask import Flask, request, jsonify, render_template
from pytube import YouTube

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video', methods=['GET'])
def video():
    video_id = request.args.get('id')
    if video_id:
        try:
            url = f'https://www.youtube.com/watch?v={video_id}'
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            return jsonify({'stream_url': stream.url})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return jsonify({'error': 'No video ID provided.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
