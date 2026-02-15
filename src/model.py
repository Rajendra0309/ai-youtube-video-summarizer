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

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}

            if len(transcript) > 60000:
                transcript = transcript[:60000] + "... (transcript truncated)"

            full_prompt = f"{prompt}\n\n{extra}\n\nVideo Transcript: {transcript}"

            data = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 20,
                    "topP": 0.9,
                    "maxOutputTokens": 8192,
                }
            }

            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)

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

    @staticmethod
    def google_gemini_video(video_url, prompt):
        """
        Robust fallback: Downloads audio via yt-dlp, uploads to Gemini File API, 
        and generates content. Bypasses YouTube transcript blocks on cloud IPs.
        """
        import google.generativeai as genai
        import tempfile
        import time
        from pathlib import Path
        import yt_dlp

        try:
            load_dotenv()
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            if not api_key:
                return "⚠️ Missing Gemini API key."

            genai.configure(api_key=api_key)

            # 1. Download Audio to Temp File
            with tempfile.TemporaryDirectory() as tmpdirname:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{tmpdirname}/%(id)s.%(ext)s',
                    'quiet': True,
                    'no_warnings': True,
                    'overwrites': True,
                }
                
                audio_path = None
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    audio_path = ydl.prepare_filename(info)

                if not audio_path or not os.path.exists(audio_path):
                    return None

                # 2. Upload to Gemini
                # Let Gemini infer MIME type from extension (e.g., .m4a, .webm)
                myfile = genai.upload_file(audio_path)
                
                # Wait for processing
                while myfile.state.name == "PROCESSING":
                    time.sleep(2)
                    myfile = genai.get_file(myfile.name)

                if myfile.state.name == "FAILED":
                    return None

                # 3. Generate Content
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(
                    [myfile, prompt],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        top_p=0.9,
                        top_k=20,
                        max_output_tokens=8192
                    )
                )
                
                # Cleanup remote file
                myfile.delete()
                
                return response.text if response else None

        except Exception as e:
            print(f"Video processing error: {e}")
            return None
