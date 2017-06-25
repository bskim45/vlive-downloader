from bs4 import BeautifulSoup
import re, os
import requests
import json
from flask import Flask, render_template, request, url_for, send_file, send_from_directory
from StringIO import StringIO
from pycaption import WebVTTReader, SRTWriter

app = Flask(__name__)

@app.route("/", methods = ['GET'])
@app.route("/<video_id>", methods = ['GET'])
def index(video_id=None):
    if video_id:
        try:
            video_list, thumbnail_url, caption_list = getVideoList(video_id)
            error = False
        except TypeError:
            video_list = thumbnail_url = caption_list = ""
            error = True
        return render_template('video_list.html', error = error, video_id = video_id, video_list = video_list, thumbnail_url = thumbnail_url, caption_list = caption_list)
    else:
        return render_template('form.html')

def getJSONURL(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = soup.findAll('script', {"type" : "text/javascript"})
    for s in scripts:
        if "vlive.video.init" in s.text:
            video_data = s.text.split("vlive.video.init(", 1)[-1].split(');', 1)[0].split(",")
            video_id = video_data[5].strip().replace('"', '')
            video_key = video_data[6].strip().replace('"', '')
            url = "http://global.apis.naver.com/rmcnmv/rmcnmv/vod_play_videoInfo.json?videoId=" + video_id + "&key=" + video_key
    return url

def getVideoList(video_id):
    video_url = "http://www.vlive.tv/video/" + video_id
    json_url = getJSONURL(video_url)
    r = requests.get(json_url)
    try:
        video_json = json.loads(r.text)
    except ValueError:
        return
    video_list = []
    for block in video_json['videos']['list']:
        video_list.append(block)
    thumbnail_url = video_json['meta']['cover']['source']
    caption_list = []
    for caption in video_json.get('captions', {}).get('list', {}):
        caption_list.append(caption)
    return video_list, thumbnail_url, caption_list

@app.route('/favicon.ico', methods = ['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/srt/<video_id>/<locale>', methods = ['GET'])
def convertSubtitle(video_id, locale="en_US"):
    url = getVTTURL(video_id, locale)
    r = requests.get(url)
    converted = convertVTTtoSRT(r.content.decode('utf-8', 'ignore'))
    strIO = StringIO()
    strIO.write(converted.encode("utf-8"))
    strIO.seek(0)
    return send_file(strIO, attachment_filename=video_id+".srt", as_attachment=True)

def getVTTURL(video_id, locale):
    _, _, caption_list = getVideoList(video_id)
    for item in caption_list:
        if item["locale"] == locale:
            return item['source']

def convertVTTtoSRT(fileContents):
    caption_set = WebVTTReader().read(fileContents)
    converted = SRTWriter().write(caption_set)
    return converted

@app.route('/video/<video_id>/<resolution>', methods = ['GET'])
@app.route('/video/<video_id>/<resolution>/<locale>', methods = ['GET'])
def watch(video_id, resolution, locale="en_US"):
    video_list, thumbnail_url, caption_list = getVideoList(video_id)
    for item in video_list:
        if item['encodingOption']['name'] == resolution:
            video_url = item['source']

    return render_template('video.html', video_url = video_url, caption_list = caption_list, locale = locale)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
