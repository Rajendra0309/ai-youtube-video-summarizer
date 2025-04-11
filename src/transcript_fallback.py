import requests
import json
import time
import os
from urllib.parse import quote

class TranscriptFallback:
    """Fallback service for when direct YouTube transcript API fails"""
    
    @staticmethod
    def get_transcript(video_id):
        """Try alternative services to get transcript"""
        
        invidious_instances = [
            "https://invidious.snopyta.org",
            "https://yewtu.be",
            "https://invidious.kavin.rocks"
        ]
        
        for instance in invidious_instances:
            try:
                captions_url = f"{instance}/api/v1/captions/{video_id}"
                response = requests.get(captions_url, timeout=5)
                
                if response.status_code == 200:
                    captions_data = response.json()
                    
                    english_caption = None
                    for caption in captions_data.get("captions", []):
                        if caption.get("language_code", "").startswith("en"):
                            english_caption = caption
                            break
                    
                    if not english_caption and captions_data.get("captions"):
                        english_caption = captions_data["captions"][0]
                    
                    if english_caption:
                        caption_url = f"{instance}/api/v1/captions/{video_id}?label={quote(english_caption.get('label', ''))}"
                        caption_response = requests.get(caption_url, timeout=5)
                        if caption_response.status_code == 200:
                            try:
                                text_content = " ".join([item.get("text", "") for item in caption_response.json()])
                                if text_content.strip():
                                    return text_content
                            except:
                                pass
            except Exception as e:
                print(f"Invidious fallback failed for {instance}: {str(e)}")
                continue
        
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        if youtube_api_key:
            try:
                api_url = f"https://www.googleapis.com/youtube/v3/captions?videoId={video_id}&part=snippet&key={youtube_api_key}"
                response = requests.get(api_url)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'items' in data and len(data['items']) > 0:
                        pass
            except:
                pass

        return None
    
    @staticmethod
    def get_transcript_with_timestamps(video_id):
        """Get transcript with timestamps using fallback services"""
        
        plain_transcript = TranscriptFallback.get_transcript(video_id)
        if plain_transcript:
            words = plain_transcript.split()
            segments = [words[i:i+20] for i in range(0, len(words), 20)]
            
            final_transcript = ""
            for i, segment in enumerate(segments):
                seconds = i * 5
                hours = seconds // 3600
                seconds %= 3600
                minutes = seconds // 60
                seconds %= 60
                timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                segment_text = " ".join(segment)
                final_transcript += f'{segment_text} "time:{timestamp}" '
                
            return final_transcript
            
        return None
