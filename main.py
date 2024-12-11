import json
import urllib.parse
import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Invidious APIのリスト
requestAPI = {
    'videos': [
        'https://invidious.nerdvpn.de/',
        'https://youtube.privacyplz.org/'
    ],
    # 他のリクエストAPIのリストも必要に応じて追加
}

def request_video_data(videoid):
    url = f"{requestAPI['videos'][0]}/videos/{urllib.parse.quote(videoid)}"
    response = requests.get(url)
    return response.json()

def getVideoData(videoid):
    t = request_video_data(videoid)

    if 'recommendedvideo' in t:
        recommended_videos = t["recommendedvideo"]
    elif 'recommendedVideos' in t:
        recommended_videos = t["recommendedVideos"]
    else:
        recommended_videos = {
            "videoId": "failed",
            "title": "failed",
            "authorId": "failed",
            "author": "failed",
            "lengthSeconds": 0,
            "viewCountText": "Load Failed"
        }

    return [
        {
            'video_urls': list(reversed([i["url"] for i in t["formatStreams"]]))[:2],
            'description_html': t["descriptionHtml"].replace("\n", "<br>"),
            'title': t["title"],
            'length_text': str(datetime.timedelta(seconds=t["lengthSeconds"])),
            'author_id': t["authorId"],
            'author': t["author"],
            'author_thumbnails_url': t["authorThumbnails"][-1]["url"],
            'view_count': t["viewCount"],
            'like_count': t["likeCount"],
            'subscribers_count': t["subCountText"]
        },
        [
            {
                "video_id": i["videoId"],
                "title": i["title"],
                "author_id": i["authorId"],
                "author": i["author"],
                "length_text": str(datetime.timedelta(seconds=i["lengthSeconds"])),
                "view_count_text": i["viewCountText"]
            } for i in recommended_videos
        ]
    ]

@app.route('/api/video/<videoid>', methods=['GET'])
def video_api(videoid):
    data = getVideoData(videoid)
    return jsonify(data)

if __name__ == '__main__':
    app.run()
