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

class Misc:
    @staticmethod
    def loaderx():
        n = randint(0, 3)  # Adjusted to use the range [0, 3] for the 4 loader messages
        loader = [
            "🔄 Loading... Hold on tight!",
            "⏳ AI is brewing your content potion...",
            "🌟 The AI is working its magic...",
            "🤖 Processing your request... AI at work!"
        ]
        return n, loader

    @staticmethod  
    def footer():
        ft = """
        <style>
        a:link , a:visited{
        color: #BFBFBF;  /* theme's text color hex code at 75 percent brightness */
        background-color: transparent;
        text-decoration: none;
        }

        a:hover, a:active {
        color: #0283C3; /* theme's primary color */
        background-color: transparent;
        text-decoration: underline;
        }

        #page-container {
        position: relative;
        min-height: 10vh;
        }

        footer {
            visibility: hidden;
        }

        .footer {
        position: relative;
        left: 0;
        top: -25px;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #808080; /* theme's text color hex code at 50 percent brightness */
        text-align: center;
        font-size: 0.9em;
        padding: 10px 0;
        }
        </style>

        <div id="page-container">
        <div class="footer">
        <p>
        By <a href="https://github.com/Rajendra0309" target="_blank">Rajendra⚡</a>
        </p>
        </div>
        </div>
        """
        return ft


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
        self.model_name = "Gemini"  # Set Gemini as the default model
        load_dotenv()

    def get_youtube_info(self):
        self.youtube_url = st.text_input(
            "Enter YouTube Video Link",
            placeholder="Paste YouTube URL here...",
            label_visibility="collapsed",  # Hide the default label to make the input cleaner
        )

        if not os.getenv("GOOGLE_GEMINI_API_KEY"):
            st.warning('⚠️ **Gemini API key is missing!** Please check your environment variables.', icon="⚠️")

        if self.youtube_url:
            self.video_id = GetVideo.Id(self.youtube_url)
            if self.video_id is None:
                st.write("**Error**")
                st.image("https://i.imgur.com/KWFtgxB.png", use_column_width=True)
                st.stop()
            self.video_title = GetVideo.title(self.youtube_url)
            st.write(f"**{self.video_title}**")

            # Add custom CSS styling for neon effect on the video
            st.markdown("""
                <style>
                .neon-video {
                    box-shadow: 0 0 5px 5px rgba(0, 255, 255, 0.5), 0 0 5px rgba(0, 255, 255, 0.5);
                    border-radius: 10px;
                    border: 1px solid rgba(0, 255, 255, 0.5);
                }
                </style>
            """, unsafe_allow_html=True)

            # Embed the YouTube video with neon effect by embedding the iframe with custom class
            video_embed_url = f"https://www.youtube.com/embed/{self.video_id}"
            st.markdown(f"""
                <iframe class="neon-video" width="100%" height="400px" src="{video_embed_url}" frameborder="0" allowfullscreen></iframe>
            """, unsafe_allow_html=True)

    def generate_summary(self):
        if st.button(":rainbow[**Get Summary**]", use_container_width=True):
            self.video_transcript = GetVideo.transcript(self.youtube_url)
            if self.model_name == "Gemini":
                self.summary = Model.google_gemini(transcript=self.video_transcript, prompt=Prompt.prompt1())
            st.markdown("## Summary:")
            st.write(self.summary)
            st_copy_to_clipboard(self.summary)

    def generate_time_stamps(self):
        if st.button(":rainbow[**Get Timestamps**]", use_container_width=True):
            self.video_transcript_time = GetVideo.transcript_time(self.youtube_url)
            youtube_url_full = f"https://youtube.com/watch?v={self.video_id}"
            if self.model_name == "Gemini":
                self.time_stamps = Model.google_gemini(self.video_transcript_time, Prompt.prompt1(ID='timestamp'), extra=youtube_url_full)
            st.markdown("## Timestamps:")
            st.markdown(self.time_stamps)
            cp_text = TimestampFormatter.format(self.time_stamps)
            st_copy_to_clipboard(cp_text)

    def generate_transcript(self):
        if st.button("Get Transcript", use_container_width=True):
            self.video_transcript = GetVideo.transcript(self.youtube_url)
            self.transcript = self.video_transcript
            st.markdown("## Transcript:")
            st.download_button(label="Download as text file", data=self.transcript, file_name=f"Transcript - {self.video_title}")
            st.write(self.transcript)
            st_copy_to_clipboard(self.transcript)

    def run(self):
        st.set_page_config(page_title="AI Video Summarizer", page_icon="chart_with_upwards_trend", layout="wide")

        # Dark purple gradient background close to black
        page_bg_img = """
        <style>
            /* Royal Color Palette */
            :root {
                --deep-purple: #4A0E4E;       /* Deep royal purple */
                --royal-gold: #D4AF37;        /* Elegant gold */
                --rich-navy: #0A2342;         /* Deep navy blue */
                --regal-crimson: #850E35;     /* Regal crimson */
                --midnight-blue: #1B264F;     /* Dark midnight blue */
            }

            /* Global Background */
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, var(--deep-purple), var(--rich-navy));
                background-attachment: fixed;
                min-height: 100vh;
            }

            /* Main App Container */
            .stApp {
                background: transparent;
            }

            /* Elegant Glassmorphic Design */
            [data-testid="stVerticalBlock"] {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                padding: 20px;
                margin-bottom: 20px;
            }

            /* Royal Title Styling */
            .title {
                text-align: center;
                font-size: 48px;
                font-weight: bold;
                background: linear-gradient(45deg, var(--royal-gold), var(--regal-crimson));
                -webkit-background-clip: text;
                color: transparent;
                margin-bottom: 30px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                animation: royal-gradient 5s ease infinite;
            }

            @keyframes royal-gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            /* Button Styling */
            .stButton>button {
                background: linear-gradient(to right, var(--royal-gold), var(--regal-crimson)) !important;
                color: white !important;
                border: none;
                border-radius: 30px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 30px;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .stButton>button:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
                background: linear-gradient(to right, var(--regal-crimson), var(--royal-gold)) !important;
            }

            /* Radio Button Styling */
            .stRadio>div {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 15px;
            }

            .stRadio [data-testid="stMarkdownContainer"] {
                color: var(--royal-gold);
                font-weight: bold;
            }

            /* Input Styling */
            .stTextInput>div>div>input {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid var(--royal-gold);
                color: white;
                border-radius: 10px;
                padding: 10px;
                transition: all 0.3s ease;
            }

            .stTextInput>div>div>input:focus {
                border-color: var(--royal-gold);
                box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
            }

            /* Spinner Styling */
            .stSpinner>div {
                border-top-color: var(--royal-gold) !important;
                border-right-color: var(--royal-gold) !important;
            }

            /* Footer Styling */
            .footer {
                color: var(--royal-gold);
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            }

            /* Scrollbar Styling */
            ::-webkit-scrollbar {
                width: 10px;
            }

            ::-webkit-scrollbar-track {
                background: var(--deep-purple);
            }

            ::-webkit-scrollbar-thumb {
                background: var(--royal-gold);
                border-radius: 5px;
            }
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)

        # Custom title with a gradient and animation
        st.markdown('<div class="title">AI Video Summarizer</div>', unsafe_allow_html=True)

        editor = ModuleEditor('st_copy_to_clipboard')
        editor.modify_frontend_files()

        # Layout with three columns: left, center, right
        self.col1, self.col2, self.col3 = st.columns([1, 2, 1])

        with self.col1:
            pass  # First column remains empty

        with self.col2:
            # Center the YouTube URL input box here (top of the center column)
            self.get_youtube_info()

            st.markdown(
                "<div class='content-container'>"
                "<p><strong><br>What do you want to generate for this video?</strong></p>"
                "</div>", unsafe_allow_html=True
            )

            mode = st.radio(
                "Choose an option:",
                [":rainbow[🪄 AI Summary]", ":rainbow[🎰 AI Timestamps]", "🔤 Transcript"],
                index=0
            )
            ran_loader = Misc.loaderx()
            n, loader = ran_loader[0], ran_loader[1]

            if mode == ":rainbow[**AI Summary**]":
                with st.spinner(loader[n]):
                    self.generate_summary()

            elif mode == ":rainbow[**AI Timestamps**]":
                with st.spinner(loader[n]):
                    self.generate_time_stamps()
            else:
                with st.spinner(loader[0]):
                    self.generate_transcript()

        # Display the footer with a cleaner style and centered text
        st.write(Misc.footer(), unsafe_allow_html=True)


if __name__ == "__main__":
    app = AIVideoSummarizer()
    app.run()
