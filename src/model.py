import os
import requests
import json
from dotenv import load_dotenv

class Model:
    @staticmethod
    def google_gemini(transcript, prompt, extra=""):
        if not transcript:
            return "⚠️ No transcript available for this video. The video may not have captions."
            
        try:
            load_dotenv()
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            
            if not api_key:
                return "⚠️ Missing Gemini API key. Please add your API key to the .env file."
            
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            
            if len(transcript) > 30000:
                transcript = transcript[:30000] + "... (transcript truncated)"
                
            full_prompt = f"{prompt}\n\n{extra}\n\nVideo Transcript: {transcript}"
            
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.4,
                    "topK": 32,
                    "topP": 0.95,
                    "maxOutputTokens": 8192,
                }
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    if "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"]:
                        parts = result["candidates"][0]["content"]["parts"]
                        texts = [part.get("text", "") for part in parts if "text" in part]
                        return "\n".join(texts)
                return "⚠️ Could not parse API response."
            else:
                error_msg = f"API error (HTTP {response.status_code})"
                try:
                    error_info = response.json()
                    if "error" in error_info and "message" in error_info["error"]:
                        error_msg += f": {error_info['error']['message']}"
                except:
                    pass
                return f"⚠️ {error_msg}"
                
        except Exception as e:
            return f"⚠️ Error with Gemini API: {str(e)}"
