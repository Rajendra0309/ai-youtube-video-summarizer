from youtube_transcript_api import YouTubeTranscriptApi 
from bs4 import BeautifulSoup
import requests
import re

class GetVideo:
    @staticmethod
    def Id(link):
        """Extracts the video ID from a YouTube video link."""
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
            
            # If all else fails, try a generic approach
            video_id = link.split("v=")[-1].split("&")[0]
            if len(video_id) == 11:
                return video_id
                
            return None
        except Exception:
            return None

    @staticmethod
    def title(link):
        """Gets the title of a YouTube video."""
        r = requests.get(link) 
        s = BeautifulSoup(r.text, "html.parser") 
        try:
            title = s.find("meta", itemprop="name")["content"]
            return title
        except TypeError:
            title = "⚠️ There seems to be an issue with the YouTube video link provided. Please check the link and try again."
            return title
        
    @staticmethod
    def transcript(link):
        """Gets the transcript of a YouTube video."""
        video_id = GetVideo.Id(link)
        try:
            if video_id is None:
                return None
            transcript_dict = YouTubeTranscriptApi.get_transcript(video_id)
            final_transcript = " ".join(i["text"] for i in transcript_dict)
            return final_transcript
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return None

    @staticmethod
    def transcript_time(link):
        """Gets the transcript of a YouTube video with timestamps."""
        video_id = GetVideo.Id(link)
        try:
            if video_id is None:
                return None
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
        except Exception as e:
            print(f"Error getting transcript with timestamps: {e}")
            return None