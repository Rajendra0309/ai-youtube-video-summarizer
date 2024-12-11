import streamlit as st
import os
from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.timestamp_formatter import TimestampFormatter
from st_copy_to_clipboard import st_copy_to_clipboard
from dotenv import load_dotenv

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
                /* Dark Theme Styles */
                .stApp {
                    background-color: #0E1117;
                    color: #FFFFFF;
                }
                .stTextInput > div > div > input {
                    color: #FFFFFF;
                    background-color: #262730;
                    border: 1px solid #4a4a4a;
                }
                .stSelectbox > div > div > div {
                    color: #FFFFFF;
                    background-color: #262730;
                }
                .stMarkdown {
                    color: #E0E0E0;
                }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
<style>
    /* Light Theme Styles */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    .stTextInput > div > div > input {
        color: #000000;
        background-color: #F0F2F6;
        border: 1px solid #D3D3D3;
    }
    .stSelectbox > div > div > div {
        color: #000000;
        background-color: #F0F2F6;
    }
    .stMarkdown {
        color: #333333;
    }
    /* Specific fix for radio button text */
    .stRadio > div > div > label {
        color: #000000 !important;
    }
    .stRadio > div {
        color: #000000 !important;
    }
    .stRadio span {
        color: #000000 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #007bff;
    }
    .stButton > button {
        color: #000000;
        background-color: #F0F2F6;
    }
    .stTextArea > div > div > textarea {
        color: #000000;
        background-color: #F0F2F6;
    }
</style>
""", unsafe_allow_html=True)

    def _theme_toggle(self):
        # Theme toggle button
        col1, col2 = st.columns([10, 1])
        with col2:
            theme_emoji = "🌞" if st.session_state.theme == 'dark' else "🌙"
            if st.button(theme_emoji):
                st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
                st.experimental_rerun()

    def get_youtube_info(self):
        # Enhanced input styling
        st.markdown("""
        <style>
        .center-container { 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            margin-bottom: 20px;
        }
        .youtube-input { 
            width: 100%; 
            padding: 15px; 
            font-size: 18px; 
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        .youtube-input:focus {
            box-shadow: 0 0 10px rgba(0,123,255,0.5);
            border-color: #007bff;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="center-container">', unsafe_allow_html=True)
        self.youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="Paste YouTube URL here...",
            label_visibility="collapsed",
            key="youtube_input"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # API Key Check with Enhanced Warning
        if not os.getenv("GOOGLE_GEMINI_API_KEY"):
            st.warning(
                "⚠️ **Gemini API key is missing!** \n\n"
                "Please set the API key in your environment variables to use this application. "
                "You can obtain an API key from the Google AI Studio."
            )
            st.stop()

        # Video Embedding with Enhanced Style
        if self.youtube_url:
            self.video_id = GetVideo.Id(self.youtube_url)
            if self.video_id is None:
                st.error("Invalid YouTube URL. Please check and try again.")
                st.stop()
            
            self.video_title = GetVideo.title(self.youtube_url)
            st.markdown(f'<h3 style="text-align: center; color: #007bff;">{self.video_title}</h3>', unsafe_allow_html=True)
            
            # Centered Video Embed with Shadow and Round Corners
            st.markdown(
                f'<div style="display: flex; justify-content: center; margin-bottom: 20px;">'
                f'<div style="'
                f'box-shadow: 0 10px 25px rgba(0,0,0,0.1); '
                f'border-radius: 15px; '
                f'background-color: white; '
                f'padding: 10px; '
                f'display: inline-block;">'
                f'<iframe width="560" height="315" '
                f'src="https://www.youtube.com/embed/{self.video_id}" '
                f'frameborder="0" '
                f'style="border-radius: 10px;" '
                f'allowfullscreen></iframe>'
                f'</div></div>', 
                unsafe_allow_html=True
            )

    def generate_summary(self):
        with st.spinner("🤖 AI is crafting a concise summary..."):
            try:
                self.video_transcript = GetVideo.transcript(self.youtube_url)
                if not self.video_transcript:
                    st.error("😔 Transcript could not be retrieved. Please check the video URL.")
                    return

                self.summary = Model.google_gemini(self.video_transcript, Prompt.prompt1())
                
                if not self.summary or not isinstance(self.summary, str):
                    st.error("🚨 Failed to generate summary. Please try again later.")
                    return

                st.markdown("### 📝 Video Summary")
                st.markdown(f'<div style="background-color: rgba(0,123,255,0.1); padding: 20px; border-radius: 10px;">{self.summary}</div>', unsafe_allow_html=True)
                st_copy_to_clipboard(self.summary)
    
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

    def generate_time_stamps(self):
        with st.spinner("🕒 Generating Timestamps..."):
            self.video_transcript_time = GetVideo.transcript_time(self.youtube_url)
            raw_timestamps = Model.google_gemini(self.video_transcript_time, Prompt.prompt1(ID='timestamp'))
        
        # Format timestamps
            formatted_timestamps = TimestampFormatter.format(raw_timestamps)
        
            st.markdown("### 🕰️ Video Timestamps")
            st.markdown(
                f'<div style="background-color: rgba(40,167,69,0.1); padding: 20px; border-radius: 10px; white-space: pre-wrap;">{formatted_timestamps}</div>', 
                unsafe_allow_html=True
            )

    def generate_transcript(self):
        with st.spinner("📝 Fetching Transcript..."):
            try:
                self.video_transcript = GetVideo.transcript(self.youtube_url)
                if not self.video_transcript:
                    st.error("😔 Transcript could not be retrieved. Please check the video URL.")
                    return

                self.transcript = self.video_transcript

                # Fixed height for the text area with scroll bar
                st.markdown("### 📄 Video Transcript")
                st.text_area(
                    "Transcript",
                    self.transcript,
                    height=500,  # Set a fixed height
                    placeholder="Transcript will appear here...",
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    def run(self):
        # Apply theme at the start of the run
        self._set_theme()

        # Theme toggle
        self._theme_toggle()

        col1, col2 = st.columns([1, 11])
        with col1:
            st.image("https://em-content.zobj.net/content/2020/04/05/yt.png", width=60)

        with col2:
            st.markdown('<h1 style="font-size: 40px; color: #007bff;">AI Video Summarizer</h1>', unsafe_allow_html=True)
        
        self.get_youtube_info()

        if self.youtube_url:
            mode = st.radio(
                "Choose Generation Mode", 
                ["Summary", "Timestamps", "Transcript"], 
                horizontal=True,
                help="Select what type of information you'd like to extract from the video."
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