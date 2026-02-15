import os
import json
import requests
from urllib.parse import urlparse, parse_qs

def is_render_env():
    return os.environ.get('RENDER') == 'true'

def extract_video_id_from_url(url):
    if not url:
        return None

    parsed_url = urlparse(url)

    if 'youtube.com' in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]

    elif 'youtu.be' in parsed_url.netloc:
        return parsed_url.path.lstrip('/')

    return None

def get_transcript_alternative(video_id):
    try:
        return None
    except Exception as e:
        print(f"Alternative transcript retrieval failed: {e}")
        return None

def get_video_title_alternative(video_id):
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        if response.status_code == 200:
            data = response.json()
            if "title" in data:
                return data["title"]
    except:
        pass

    return f"Video {video_id}"
