import json
import urllib.parse
import datetime
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Invidious API URLs
requestAPI_urls = [
r"https://inv.vern.cc/",
r"https://inv.zzls.xyz/",
r"https://invi.susurrando.com/",
r"https://invidious.epicsite.xyz/",
r"https://invidious.esmailelbob.xyz/",
r"https://invidious.garudalinux.org/",
r"https://invidious.kavin.rocks/",
r"https://invidious.lidarshield.cloud/",
r"https://invidious.lunar.icu/",
r"https://yt-us.discard.no/",
r"https://invidious.nerdvpn.de/",
r"https://invidious.privacydev.net/",
r"https://invidious.sethforprivacy.com/",
r"https://invidious.slipfox.xyz/",
r"https://yt-no.discard.no/",
r"https://invidious.snopyta.org/",
r"https://invidious.tiekoetter.com/",
r"https://invidious.vpsburti.com/",
r"https://invidious.weblibre.org/",
r"https://invidious.pufe.org/",
r"https://iv.ggtyler.dev/",
r"https://iv.melmac.space/",
r"https://vid.puffyan.us/",
r"https://watch.thekitty.zone/",
r"https://yewtu.be/",
r"https://youtube.moe.ngo/",
r"https://yt.31337.one/",
r"https://yt.funami.tech/",
r"https://yt.oelrichsgarcia.de/",
r"https://yt.wkwkwk.fun/",
r"https://youtube.076.ne.jp/",
r"https://invidious.projectsegfau.lt/",
r"https://invidious.fdn.fr/",
r"https://i.oyster.men/",
r"https://invidious.domain.glass/",
r"https://inv.skrep.eu/",
r"https://clips.im.allmendenetz.de/",
r"https://ytb.trom.tf/",
r"https://invidious.pcgamingfreaks.at/",
r"https://youtube.notrack.ch/",
r"https://iv.ok0.org/",
r"https://youtube.vpn-home-net.de/",
r"http://144.126.251.186/",
r"https://invidious.citizen4.eu/",
r"https://yt.sebaorrego.net/",
r"https://invidious.pesso.al/",
r"https://invidious.manasiwibi.com/",
r"https://toob.unternet.org/",
r"https://youtube.mosesmang.com/",
r"https://invidious.varishangout.net/",
r"https://invidio.xamh.de/",
r"https://yt.tesaguri.club/",
r"https://video.francevpn.fr/",
r"https://inv.in.projectsegfau.lt/",
r"https://invid.nevaforget.de/",
r"https://tube.foss.wtf/",
r"https://invidious.777.tf/",
r"https://inv.tux.pizza/",
r"https://youtube.076.ne.jp",
r"https://invidious.osi.kr/",
r"https://inv.riverside.rocks/",
r"https://inv.bp.mutahar.rocks/",
r"https://invidious.namazso.eu/",
r"https://tube.cthd.icu/",
r"https://invidious.snopyta.org/",
r"https://yewtu.be/",
r"https://invidious.privacy.gd/",
r"https://invidious.lunar.icu/",
r"https://vid.puffyan.us/",
r"https://invidious.weblibre.org/",
r"https://invidious.esmailelbob.xyz/",
r"https://invidio.xamh.de/",
r"https://invidious.kavin.rocks/",
r"https://invidious-us.kavin.rocks/",
r"https://invidious.mutahar.rocks/",
r"https://invidious.zee.li/",
r"https://tube.connect.cafe/",
r"https://invidious.zapashcanon.fr/",
r"https://invidious.poast.org/",
r"https://ytb.trom.tf/",
r"https://invidious.froth.zone/",
r"https://invidious.domain.glass/",
r"https://invidious.sp-codes.de/",
r"http://144.126.251.186/",
r"https://yt.512mb.org/",
r"https://invidious.fdn.fr/",
r"https://invidious.pcgamingfreaks.at/",
r"https://tube.meowz.moe/",
r"https://clips.im.allmendenetz.de/",
r"https://inv.skrep.eu/",
r"https://invidious.frbin.com/",
r"https://dev.invidio.us/",
r"https://invidious.site/",
r"https://invidious.sethforprivacy.com/",
r"https://invidious.stemy.me/",
r"https://betamax.cybre.club/",
r"https://invidious.com/",
r"https://invidious.snopyta.org",
r"https://yewtu.be",
r"https://invidious.kavin.rocks",
r"https://vid.puffyan.us",
r"https://inv.riverside.rocks",
r"https://invidious.not.futbol/",
r"https://youtube.076.ne.jp",
r"https://yt.artemislena.eu",
r"https://invidious.esmailelbob.xyz",
r"https://invidious.projectsegfau.lt",
r"https://invidious.dhusch.de/",
r"https://inv.odyssey346.dev/"
]

def requestAPI(endpoint):
    for base_url in requestAPI_urls:
        try:
            response = httpx.get(f"{base_url}{endpoint}")
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return None

def getVideoData(videoid):
    response_text = requestAPI(f"/videos/{urllib.parse.quote(videoid)}")
    
    if response_text is None:
        raise HTTPException(status_code=404, detail="Video not found")

    try:
        t = json.loads(response_text)

        if 'recommendedvideo' in t:
            recommended_videos = t["recommendedvideo"]
        elif 'recommendedVideos' in t:
            recommended_videos = t["recommendedVideos"]
        else:
            recommended_videos = [{
                "videoId": "failed",
                "title": "failed",
                "authorId": "failed",
                "author": "failed",
                "lengthSeconds": 0,
                "viewCountText": "Load Failed"
            }]
        
        # Prepare the main video data
        video_data = {
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
        }

        # Prepare recommended videos data
        recommended_videos_data = [
            {
                "video_id": i["videoId"],
                "title": i["title"],
                "author_id": i["authorId"],
                "author": i["author"],
                "length_text": str(datetime.timedelta(seconds=i["lengthSeconds"])),
                "view_count_text": i["viewCountText"]
            } for i in recommended_videos
        ]

        return video_data, recommended_videos_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to decode JSON response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/video/{videoid}")
async def get_video(videoid: str):
    video_data, recommended_videos_data = getVideoData(videoid)
    
    return {
        "video_data": video_data,
        "recommended_videos": recommended_videos_data
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the Video API! Use the /video/{videoid} endpoint to fetch video details."}

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
