from youtube_transcript_api import YouTubeTranscriptApi 
from bs4 import BeautifulSoup
import requests
import re
import json
import os
from urllib.parse import urlparse, parse_qs
import time

class GetVideo:
    @staticmethod
    def Id(link):
        """Extracts the video ID from a YouTube video link."""
        try:
            if not link:
                return None
                
            parsed_url = urlparse(link)
            
            if 'youtube.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return query_params['v'][0]
                    
                path_parts = parsed_url.path.split('/')
                if len(path_parts) >= 3 and path_parts[1] == 'embed':
                    return path_parts[2]
                
            elif 'youtu.be' in parsed_url.netloc:
                path_parts = parsed_url.path.split('/')
                if len(path_parts) >= 2:
                    return path_parts[1]
            
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
            
            if "v=" in link:
                video_id = link.split("v=")[-1].split("&")[0]
                if len(video_id) == 11:
                    return video_id
                
            return None
        except Exception as e:
            print(f"Error extracting video ID: {str(e)}")
            return None

    @staticmethod
    def title(link):
        """Gets the title of a YouTube video using multiple methods."""
        video_id = GetVideo.Id(link)
        if not video_id:
            return "⚠️ Could not extract video ID from the URL."
            
        try:
            try:
                oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(oembed_url, headers=headers)
                if response.status_code == 200:
                    oembed_data = response.json()
                    if "title" in oembed_data:
                        return oembed_data["title"]
            except Exception as e:
                print(f"oEmbed method failed: {str(e)}")
            
            youtube_api_key = os.getenv("YOUTUBE_API_KEY")
            if youtube_api_key:
                try:
                    api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet&key={youtube_api_key}"
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        data = response.json()
                        if 'items' in data and len(data['items']) > 0:
                            return data['items'][0]['snippet']['title']
                except Exception as e:
                    print(f"YouTube API method failed: {str(e)}")
            
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9"
                }
                
                invidious_instances = [
                    "https://invidious.snopyta.org",
                    "https://yewtu.be",
                    "https://invidious.kavin.rocks"
                ]
                
                for instance in invidious_instances:
                    try:
                        inv_url = f"{instance}/api/v1/videos/{video_id}"
                        inv_response = requests.get(inv_url, timeout=5)
                        if inv_response.status_code == 200:
                            inv_data = inv_response.json()
                            if "title" in inv_data:
                                return inv_data["title"]
                    except:
                        continue
                
                watch_url = f"https://www.youtube.com/watch?v={video_id}"
                response = requests.get(watch_url, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    for meta in soup.find_all("meta"):
                        if meta.get("property") == "og:title" and meta.get("content"):
                            return meta["content"]
                        if meta.get("name") == "title" and meta.get("content"):
                            return meta["content"]
                
                    if soup.title:
                        title_text = soup.title.string
                        if title_text and " - YouTube" in title_text:
                            return title_text.split(" - YouTube")[0].strip()
            except Exception as e:
                print(f"Web scraping method failed: {str(e)}")
            
            return f"YouTube Video ({video_id})"
            
        except Exception as e:
            print(f"Error getting video title: {str(e)}")
            return f"YouTube Video ({video_id})"
        
    @staticmethod
    def transcript(link):
        """Gets the transcript of a YouTube video with multiple fallbacks."""
        video_id = GetVideo.Id(link)
        if not video_id:
            return None
            
        for attempt in range(3):  # Try up to 3 times
            try:
                languages = ['en', 'en-US', 'en-GB', 'auto']
                
                for lang in languages:
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        
                        try:
                            transcript = transcript_list.find_manually_created_transcript(languages=[lang])
                            transcript_dict = transcript.fetch()
                            return " ".join(i["text"] for i in transcript_dict)
                        except:
                            for transcript in transcript_list:
                                try:
                                    transcript_dict = transcript.fetch()
                                    return " ".join(i["text"] for i in transcript_dict)
                                except:
                                    continue
                    except:
                        continue
                
                try:
                    transcript_dict = YouTubeTranscriptApi.get_transcript(video_id)
                    return " ".join(i["text"] for i in transcript_dict)
                except:
                    pass
                
                youtube_api_key = os.getenv("YOUTUBE_API_KEY")
                if youtube_api_key:
                    try:
                        api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=contentDetails&key={youtube_api_key}"
                        response = requests.get(api_url)
                        if response.status_code == 200:
                            data = response.json()
                            if ('items' in data and len(data['items']) > 0 and 
                                'contentDetails' in data['items'][0] and
                                'caption' in data['items'][0]['contentDetails'] and
                                data['items'][0]['contentDetails']['caption'] == 'true'):
                                try:
                                    transcript_dict = YouTubeTranscriptApi.get_transcript(video_id)
                                    return " ".join(i["text"] for i in transcript_dict)
                                except:
                                    pass
                    except:
                        pass
                        
            except Exception as e:
                print(f"Transcript attempt {attempt+1} failed: {str(e)}")
                time.sleep(1)  
        return None

    @staticmethod
    def transcript_time(link):
        """Gets the transcript of a YouTube video with timestamps."""
        video_id = GetVideo.Id(link)
        if not video_id:
            return None
            
        for attempt in range(3): 
            try:
                languages = ['en', 'en-US', 'en-GB', 'auto']
                
                for lang in languages:
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        transcript_dict = None
                        try:
                            transcript = transcript_list.find_manually_created_transcript(languages=[lang])
                            transcript_dict = transcript.fetch()
                        except:
                            for transcript in transcript_list:
                                try:
                                    transcript_dict = transcript.fetch()
                                    break
                                except:
                                    continue
                                    
                        if transcript_dict:
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
                
                try:
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
                except:
                    pass
                    
            except Exception as e:
                print(f"Transcript with timestamps attempt {attempt+1} failed: {str(e)}")
                time.sleep(1) 
        return None