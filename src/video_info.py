from youtube_transcript_api import YouTubeTranscriptApi 
from bs4 import BeautifulSoup
import requests
import re
import json
import time

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
    def transcript(link):
        video_id = GetVideo.Id(link)
        if not video_id:
            return None
            
        try:
            languages = ['en', 'en-US', 'en-GB', 'auto']
            
            for lang in languages:
                try:
                    transcript_dict = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                    return " ".join(i["text"] for i in transcript_dict)
                except:
                    continue
                    
            transcript_dict = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join(i["text"] for i in transcript_dict)
        except Exception:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for transcript in transcript_list:
                    try:
                        transcript_dict = transcript.fetch()
                        return " ".join(i["text"] for i in transcript_dict)
                    except:
                        continue
            except Exception:
                return None
                
        return None

    @staticmethod
    def transcript_time(link):
        video_id = GetVideo.Id(link)
        if not video_id:
            return None
            
        try:
            languages = ['en', 'en-US', 'en-GB', 'auto']
            
            for lang in languages:
                try:
                    transcript_dict = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                    final_transcript = ""
                    for i in transcript_dict:
                        timevar = round(float(i["start"]))
                        hours = int(timevar // 3600)
                        timevar %= 3600
                        minutes = int(timevar // 60)
                        timevar %= 60
                        timevex = f"{hours:02d}:{minutes:02d}:{timevar:02d}"
                        final_transcript += f'{i["text"]} "time:{timevex}" '
                    return final_transcript
                except:
                    continue
                    
            transcript_dict = YouTubeTranscriptApi.get_transcript(video_id)
            final_transcript = ""
            for i in transcript_dict:
                timevar = round(float(i["start"]))
                hours = int(timevar // 3600)
                timevar %= 3600
                minutes = int(timevar // 60)
                timevar %= 60
                timevex = f"{hours:02d}:{minutes:02d}:{timevar:02d}"
                final_transcript += f'{i["text"]} "time:{timevex}" '
            return final_transcript
        except Exception:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for transcript in transcript_list:
                    try:
                        transcript_dict = transcript.fetch()
                        final_transcript = ""
                        for i in transcript_dict:
                            timevar = round(float(i["start"]))
                            hours = int(timevar // 3600)
                            timevar %= 3600
                            minutes = int(timevar // 60)
                            timevar %= 60
                            timevex = f"{hours:02d}:{minutes:02d}:{timevar:02d}"
                            final_transcript += f'{i["text"]} "time:{timevex}" '
                        return final_transcript
                    except:
                        continue
            except Exception:
                return None
                
        return None