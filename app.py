import streamlit as st
import os
from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.timestamp_formatter import TimestampFormatter
from src.copy_module_edit import ModuleEditor
from dotenv import load_dotenv
from st_copy_to_clipboard import st_copy_to_clipboard
from random import randint

class AIVideoSummarizer:
    def __init__(self):
        self.youtube_url = None
        self.video_id = None
        self.video_title = None
        self.video_transcript = None
        self.video_transcript_time = None
        self.summary = None
        self.time_stamps = None
        self.transcript = None
        self.model_name = "Gemini"
        load_dotenv()

    def get_youtube_info(self):
        # Custom CSS to center and style the input
        st.markdown("""
        <style>
        .center-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
        }
        .youtube-input {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border-radius: 10px;
            border: 2px solid #4A0E4E;
            margin-bottom: 20px;
        }
        .video-container {
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 15px;
            overflow: hidden;
        }
        </style>
        """, unsafe_allow_html=True)

        # Centered input container
        st.markdown('<div class="center-container">', unsafe_allow_html=True)
        self.youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="Paste YouTube URL here...",
            label_visibility="collapsed",
            key="youtube_url_input",
            help="Paste a valid YouTube video URL",
            # Add custom CSS class
            on_change=None,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if not os.getenv("GOOGLE_GEMINI_API_KEY"):
            st.warning('⚠️ **Gemini API key is missing!** Please check your environment variables.', icon="⚠️")

        if self.youtube_url:
            self.video_id = GetVideo.Id(self.youtube_url)
            if self.video_id is None:
                st.error("Invalid YouTube URL")
                st.image("https://i.imgur.com/KWFtgxB.png", use_column_width=True)
                st.stop()
            
            self.video_title = GetVideo.title(self.youtube_url)
            
            # Centered video container
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            st.markdown(f"#### {self.video_title}", unsafe_allow_html=True)
            
            # Embed YouTube video
            video_embed_url = f"https://www.youtube.com/embed/{self.video_id}"
            st.components.v1.iframe(video_embed_url, height=450, width=800)
            st.markdown('</div>', unsafe_allow_html=True)

    def generate_options(self):
        # Custom CSS for mode selection
        st.markdown("""
        <style>
        .option-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            margin-bottom: 20px;
            width: 100%;
        }
        .option-btn {
            flex: 1;
            max-width: 250px;
            padding: 15px;
            text-align: center;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .option-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
        }
        .summary-btn {
            background: linear-gradient(135deg, #6A5ACD, #8A2BE2);
            color: white;
        }
        .timestamps-btn {
            background: linear-gradient(135deg, #20B2AA, #00CED1);
            color: white;
        }
        .transcript-btn {
            background: linear-gradient(135deg, #DAA520, #FFD700);
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

        # Centered options container
        st.markdown('<div class="option-container">', unsafe_allow_html=True)
        
        # Create columns for buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            summary_btn = st.button(
                "🪄 AI Summary", 
                key="summary_btn", 
                use_container_width=True, 
                type="primary"
            )
        
        with col2:
            timestamps_btn = st.button(
                "🎰 AI Timestamps", 
                key="timestamps_btn", 
                use_container_width=True, 
                type="primary"
            )
        
        with col3:
            transcript_btn = st.button(
                "🔤 Full Transcript", 
                key="transcript_btn", 
                use_container_width=True, 
                type="primary"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Determine which button was pressed
        if summary_btn:
            return "summary"
        elif timestamps_btn:
            return "timestamps"
        elif transcript_btn:
            return "transcript"
        return None

    def generate_summary(self):
        with st.spinner("Generating Summary..."):
            self.video_transcript = GetVideo.transcript(self.youtube_url)
            if self.model_name == "Gemini":
                self.summary = Model.google_gemini(transcript=self.video_transcript, prompt=Prompt.prompt1())
            
            st.markdown("### Video Summary")
            st.write(self.summary)
            st_copy_to_clipboard(self.summary)

    def generate_time_stamps(self):
        with st.spinner("Generating Timestamps..."):
            self.video_transcript_time = GetVideo.transcript_time(self.youtube_url)
            youtube_url_full = f"https://youtube.com/watch?v={self.video_id}"
            
            if self.model_name == "Gemini":
                self.time_stamps = Model.google_gemini(self.video_transcript_time, Prompt.prompt1(ID='timestamp'), extra=youtube_url_full)
            
            st.markdown("### Video Timestamps")
            st.markdown(self.time_stamps)
            cp_text = TimestampFormatter.format(self.time_stamps)
            st_copy_to_clipboard(cp_text)

    def generate_transcript(self):
        with st.spinner("Fetching Transcript..."):
            self.video_transcript = GetVideo.transcript(self.youtube_url)
            self.transcript = self.video_transcript
            
            st.markdown("### Video Transcript")
            st.download_button(
                label="Download Transcript", 
                data=self.transcript, 
                file_name=f"Transcript - {self.video_title}.txt",
                use_container_width=True
            )
            st.text_area("Transcript", self.transcript, height=300)
            st_copy_to_clipboard(self.transcript)

    def run(self):
        # Page configuration
        st.set_page_config(
            page_title="AI Video Summarizer", 
            page_icon="🎬", 
            layout="wide", 
            initial_sidebar_state="collapsed"
        )

        # Custom page styling
        st.markdown("""
        <style>
        .stApp {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            overflow: hidden; /* Hides the scrollbars */
        }
        </style>
        """, unsafe_allow_html=True)


        # Main title
        st.title("🎬 AI Video Summarizer")

        # Main workflow
        self.get_youtube_info()

        # Check if a YouTube URL is entered
        if self.youtube_url:
            # Generate options and get selected mode
            selected_mode = self.generate_options()

            # Generate content based on selected mode
            if selected_mode == "summary":
                self.generate_summary()
            elif selected_mode == "timestamps":
                self.generate_time_stamps()
            elif selected_mode == "transcript":
                self.generate_transcript()


if __name__ == "__main__":
    app = AIVideoSummarizer()
    app.run()