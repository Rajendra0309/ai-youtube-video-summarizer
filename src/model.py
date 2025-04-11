import os
from dotenv import load_dotenv
import requests
import json

class Model:
    def __init__(self):
        load_dotenv()

    @staticmethod
    def google_gemini(transcript, prompt, extra=""):
        """
        Generate content using Google's Gemini API
        
        Args:
            transcript (str): The video transcript text
            prompt (str): The prompt template
            extra (str): Additional context or instructions
            
        Returns:
            str: Generated content or error message
        """
        if not transcript:
            return "⚠️ No transcript available for this video. The video may not have captions."
            
        try:
            load_dotenv()
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            
            if not api_key:
                return "⚠️ Missing Gemini API key. Please add your API key to the .env file."
            
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            d
            if len(transcript) > 30000:
                transcript = transcript[:30000] + "... (transcript truncated)"
                
            full_prompt = f"{prompt}\n\n{extra}\n\nVideo Transcript: {transcript}"
            
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }]
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    if "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"]:
                        parts = result["candidates"][0]["content"]["parts"]
                        texts = [part.get("text", "") for part in parts if "text" in part]
                        return "\n".join(texts)
                return "⚠️ Unexpected response format from Gemini API."
            else:
                if response.status_code == 404:
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
                    response = requests.post(url, headers=headers, data=json.dumps(data))
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "candidates" in result and len(result["candidates"]) > 0:
                            if "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"]:
                                parts = result["candidates"][0]["content"]["parts"]
                                texts = [part.get("text", "") for part in parts if "text" in part]
                                return "\n".join(texts)
                
                error_msg = f"API Error (HTTP {response.status_code})"
                try:
                    error_detail = response.json()
                    if "error" in error_detail and "message" in error_detail["error"]:
                        error_msg += f": {error_detail['error']['message']}"
                except:
                    pass
                
                return f"⚠️ {error_msg}"
                
        except Exception as e:
            return f"⚠️ Error with Gemini API: {str(e)}"
