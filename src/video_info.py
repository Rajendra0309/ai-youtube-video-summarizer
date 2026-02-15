from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import requests
import re
import json
import html
import xml.etree.ElementTree as ET

LANGUAGE_PRIORITIES = [
    'en', 'en-US', 'en-GB', 'en-IN',
    'hi', 'bn', 'te', 'ta', 'mr', 'gu', 'kn', 'ml', 'pa', 'or', 'as', 'ur',
    'es', 'fr', 'de', 'pt', 'it', 'ru', 'ja', 'ko', 'zh', 'zh-CN', 'zh-TW',
    'ar', 'tr', 'nl', 'pl', 'sv', 'vi', 'th', 'id', 'ms', 'fi', 'no', 'da',
    'cs', 'ro', 'hu', 'el', 'he', 'uk', 'fa', 'sr', 'hr', 'bg', 'sk', 'sl',
    'lt', 'lv', 'et', 'sw', 'fil', 'ne', 'si', 'my', 'km', 'lo', 'ka', 'am',
]

class GetVideo:
    @staticmethod
    def Id(link):
        try:
            if "youtube.com" in link:
                pattern = r'(?:youtube\.com/watch\?v=|youtube\.com/embed/|youtube\.com/v/|youtube\.com/\?v=)([a-zA-Z0-9_-]+)'
                match = re.search(pattern, link)
                if match:
                    return match.group(1)
            elif "youtu.be" in link:
                pattern = r'youtu\.be/([a-zA-Z0-9_-]+)'
                match = re.search(pattern, link)
                if match:
                    return match.group(1)

            video_id = link.split("v=")[-1].split("&")[0]
            if len(video_id) == 11:
                return video_id

            return None
        except Exception:
            return None

    @staticmethod
    def title(link):
        video_id = GetVideo.Id(link)
        if not video_id:
            return None

        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = requests.get(oembed_url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "title" in data:
                    return data["title"]

        except Exception:
            pass

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }

            response = requests.get(f"https://www.youtube.com/watch?v={video_id}", headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                for meta in soup.find_all("meta"):
                    if meta.get("property") == "og:title" and meta.get("content"):
                        return meta["content"]

                if soup.title:
                    title_text = soup.title.string
                    if title_text and " - YouTube" in title_text:
                        return title_text.split(" - YouTube")[0].strip()
        except Exception:
            pass

        return f"YouTube Video ({video_id})"

    @staticmethod
    def _build_lang_list(preferred_lang=None):
        langs = []
        if preferred_lang and preferred_lang != "auto":
            langs.append(preferred_lang)
            for variant in [f"{preferred_lang}-IN", f"{preferred_lang}-US", f"{preferred_lang}-GB"]:
                langs.append(variant)
        for lang in LANGUAGE_PRIORITIES:
            if lang not in langs:
                langs.append(lang)
        return langs

    @staticmethod
    def _transcript_via_api(video_id, preferred_lang=None):
        ytt_api = YouTubeTranscriptApi()
        langs = GetVideo._build_lang_list(preferred_lang)

        try:
            for lang in langs:
                try:
                    fetched = ytt_api.fetch(video_id, languages=[lang])
                    return [{"text": snippet.text, "start": snippet.start} for snippet in fetched]
                except Exception:
                    continue

            fetched = ytt_api.fetch(video_id)
            return [{"text": snippet.text, "start": snippet.start} for snippet in fetched]
        except Exception:
            try:
                transcript_list = ytt_api.list(video_id)
                for transcript in transcript_list:
                    try:
                        fetched = transcript.fetch()
                        return [{"text": snippet.text, "start": snippet.start} for snippet in fetched]
                    except Exception:
                        continue
            except Exception:
                return None
        return None

    @staticmethod
    def _transcript_via_page_scrape(video_id, preferred_lang=None):
        try:
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            })

            url = f"https://www.youtube.com/watch?v={video_id}"
            resp = session.get(url, timeout=15)

            if resp.status_code != 200:
                return None

            player_match = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.+?\})\s*;', resp.text)
            if not player_match:
                return None

            player_data = json.loads(player_match.group(1))
            captions = player_data.get("captions", {})
            renderer = captions.get("playerCaptionsTracklistRenderer", {})
            tracks = renderer.get("captionTracks", [])

            if not tracks:
                return None

            langs = GetVideo._build_lang_list(preferred_lang)

            chosen_track = None
            for lang in langs:
                for track in tracks:
                    if track.get("languageCode") == lang and track.get("kind") != "asr":
                        chosen_track = track
                        break
                if chosen_track:
                    break

            if not chosen_track:
                for lang in langs:
                    for track in tracks:
                        if track.get("languageCode") == lang:
                            chosen_track = track
                            break
                    if chosen_track:
                        break

            if not chosen_track:
                chosen_track = tracks[0]

            base_url = chosen_track.get("baseUrl", "")
            if not base_url:
                return None

            cap_resp = session.get(base_url, timeout=15)
            if cap_resp.status_code != 200:
                return None

            root = ET.fromstring(cap_resp.text)
            segments = []
            for elem in root.findall(".//text"):
                t = elem.text or ""
                t = html.unescape(t).replace("\n", " ").strip()
                start = float(elem.get("start", "0"))
                if t:
                    segments.append({"text": t, "start": start})

            return segments if segments else None

        except Exception:
            return None

    @staticmethod
    def _transcript_via_ytdlp(video_id, preferred_lang=None):
        try:
            import yt_dlp
            import tempfile
            import glob
            import os
            import shutil

            tmpdir = tempfile.mkdtemp()

            sub_langs = []
            if preferred_lang and preferred_lang != "auto":
                sub_langs.append(preferred_lang)
            sub_langs.append("en")

            ydl_opts = {
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": sub_langs,
                "subtitlesformat": "json3",
                "outtmpl": os.path.join(tmpdir, "%(id)s"),
                "quiet": True,
                "no_warnings": True,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

                files = glob.glob(os.path.join(tmpdir, "*.json3"))
                if files:
                    with open(files[0], "r") as fp:
                        data = json.load(fp)
                    events = data.get("events", [])
                    segments = []
                    for event in events:
                        segs = event.get("segs", [])
                        text = "".join(seg.get("utf8", "") for seg in segs).strip()
                        text = re.sub(r"\n", " ", text)
                        start_ms = event.get("tStartMs", 0)
                        if text and text != " ":
                            segments.append({"text": text, "start": start_ms / 1000.0})
                    return segments if segments else None
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)

        except Exception:
            return None

    @staticmethod
    def transcript(link, preferred_lang=None):
        video_id = GetVideo.Id(link)
        if not video_id:
            return None

        segments = GetVideo._transcript_via_api(video_id, preferred_lang)

        if not segments:
            segments = GetVideo._transcript_via_page_scrape(video_id, preferred_lang)

        if not segments:
            segments = GetVideo._transcript_via_ytdlp(video_id, preferred_lang)

        if segments:
            # Group segments into paragraphs based on time gaps
            paragraphs = []
            current_para = []
            prev_end = 0

            for s in segments:
                start = float(s.get("start", 0))
                text = s["text"].strip()
                if not text:
                    continue

                # If gap > 2 seconds, start a new paragraph
                if current_para and (start - prev_end) > 2.0:
                    paragraphs.append(" ".join(current_para))
                    current_para = []

                current_para.append(text)
                # Estimate end time: start + rough duration per segment
                prev_end = start + 3.0

            if current_para:
                paragraphs.append(" ".join(current_para))

            return "\n\n".join(paragraphs)

        return None

    @staticmethod
    def transcript_time(link, preferred_lang=None):
        video_id = GetVideo.Id(link)
        if not video_id:
            return None

        segments = GetVideo._transcript_via_api(video_id, preferred_lang)

        if not segments:
            segments = GetVideo._transcript_via_page_scrape(video_id, preferred_lang)

        if not segments:
            segments = GetVideo._transcript_via_ytdlp(video_id, preferred_lang)

        if segments:
            final_transcript = ""
            for s in segments:
                timevar = round(float(s["start"]))
                hours = int(timevar // 3600)
                timevar %= 3600
                minutes = int(timevar // 60)
                timevar %= 60
                timevex = f"{hours:02d}:{minutes:02d}:{timevar:02d}"
                final_transcript += f'{s["text"]} "time:{timevex}" '
            return final_transcript

        return None