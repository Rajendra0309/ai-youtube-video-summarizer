import streamlit as st
import os
import re
from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.timestamp_formatter import TimestampFormatter
from st_copy_to_clipboard import st_copy_to_clipboard
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set page config at the very beginning
st.set_page_config(
    page_title="AI Video Summarizer", 
    page_icon="🎥", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

class AIVideoSummarizer:
    def __init__(self):
        # Initialize session state for theme
        if 'theme' not in st.session_state:
            st.session_state.theme = 'dark'

        self.youtube_url = None
        self.video_id = None
        self.video_title = ""
        self.video_transcript = ""
        self.video_transcript_time = ""
        self.summary = ""
        self.time_stamps = ""
        self.transcript = ""
        self.model_name = "Gemini"
        load_dotenv()

    def _set_theme(self):
        # Custom CSS for theme toggle
        if st.session_state.theme == 'dark':
            st.markdown("""
            <style>
                .stApp { background-color: #0E1117; color: #FFFFFF; }
                .stTextInput > div > div > input { color: #FFFFFF; background-color: #262730; border: 1px solid #4a4a4a; }
                .stMarkdown { color: #E0E0E0; }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
                .stApp { background-color: #FFFFFF; color: #000000; }
                .stTextInput > div > div > input { color: #000000; background-color: #F0F2F6; border: 1px solid #D3D3D3; }
                .stMarkdown { color: #333333; }
            </style>
            """, unsafe_allow_html=True)

    def _theme_toggle(self):
        col1, col2 = st.columns([10, 1])
        with col2:
            theme_emoji = "🌞" if st.session_state.theme == 'dark' else "🌙"
            if st.button(theme_emoji):
                st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
                st.experimental_rerun()

    def _parse_youtube_url(self, url):
        patterns = [
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
            r'(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1).split('&')[0].split('?')[0]
                return video_id
        return None

    def get_youtube_info(self):
        self.youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="Paste YouTube URL here...",
            label_visibility="collapsed",
            key="youtube_input"
        )
        if not os.getenv("GOOGLE_GEMINI_API_KEY"):
            st.warning(
                "⚠️ **Gemini API key is missing!** \n"
                "Please set the API key in your environment variables to use this application."
            )
            st.stop()

        if self.youtube_url:
            self.video_id = self._parse_youtube_url(self.youtube_url)
            if self.video_id is None:
                st.error("Invalid YouTube URL. Please check and try again.")
                st.stop()

            try:
                self.video_title = GetVideo.title(self.youtube_url)
                st.markdown(f'<h3 style="text-align: center; color: #007bff;">{self.video_title}</h3>', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="text-align: center;">'
                    f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{self.video_id}" frameborder="0" allowfullscreen></iframe>'
                    f'</div>', 
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Failed to retrieve video information: {e}")
                logging.error(f"Error fetching video title: {e}")

    def generate_summary(self):
        with st.spinner("🤖 AI is crafting a concise summary..."):
            try:
                self.video_transcript = GetVideo.transcript(self.youtube_url)
                if not self.video_transcript:
                    st.error("😔 Transcript could not be retrieved. Please check the video URL.")
                    return

                self.summary = Model.google_gemini(self.video_transcript, Prompt.prompt1())
                if not self.summary:
                    st.error("🚨 Failed to generate summary. Please try again later.")
                    return

                st.markdown("### 📝 Video Summary")
                st.markdown(f'<div style="background-color: rgba(0,123,255,0.1); padding: 20px; border-radius: 10px;">{self.summary}</div>', unsafe_allow_html=True)
                st_copy_to_clipboard(self.summary)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                logging.error(f"Error generating summary: {e}")

    def generate_time_stamps(self):
        with st.spinner("🕒 Generating Timestamps..."):
            try:
                self.video_transcript_time = GetVideo.transcript_time(self.youtube_url)
                raw_timestamps = Model.google_gemini(self.video_transcript_time, Prompt.prompt1(ID='timestamp'))
                formatted_timestamps = TimestampFormatter.format(raw_timestamps)

                st.markdown("### 🕰️ Video Timestamps")
                st.markdown(
                    f'<div style="background-color: rgba(40,167,69,0.1); padding: 20px; border-radius: 10px; white-space: pre-wrap;">{formatted_timestamps}</div>', 
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
                logging.error(f"Error generating timestamps: {e}")

    def generate_transcript(self):
        with st.spinner("📝 Fetching Transcript..."):
            try:
                self.video_transcript = GetVideo.transcript(self.youtube_url)
                if not self.video_transcript:
                    st.error("😔 Transcript could not be retrieved. Please check the video URL.")
                    return

                st.markdown("### 📄 Video Transcript")
                st.text_area(
                    "Transcript",
                    self.video_transcript,
                    height=500,
                    placeholder="Transcript will appear here...",
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
                logging.error(f"Error fetching transcript: {e}")

    def run(self):
        self._set_theme()
        self._theme_toggle()

        st.markdown('<h1 style="font-size: 40px; color: #007bff;">AI Video Summarizer</h1>', unsafe_allow_html=True)
        self.get_youtube_info()

        if self.youtube_url:
            mode = st.radio(
                "Choose Generation Mode", 
                ["Summary", "Timestamps", "Transcript"], 
                horizontal=True
            )
            if mode == "Summary":
                self.generate_summary()
            elif mode == "Timestamps":
                self.generate_time_stamps()
            elif mode == "Transcript":
                self.generate_transcript()

if __name__ == "__main__":
    app = AIVideoSummarizer()
    app.run()
