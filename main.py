from flask import Flask, request, jsonify
from pytube import YouTube

app = Flask(__name__)

@app.route('/video', methods=['GET'])
def get_video_stream():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400
    
    try:
        yt = YouTube(video_id)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        stream_url = stream.url
        return jsonify({'stream_url': stream_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
