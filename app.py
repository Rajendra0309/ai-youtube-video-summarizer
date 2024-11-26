import streamlit as st
import os
from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.timestamp_formatter import TimestampFormatter
from st_copy_to_clipboard import st_copy_to_clipboard
from dotenv import load_dotenv


class AIVideoSummarizer:
    def __init__(self):
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

    def get_youtube_info(self):
        # Input container styling
        st.markdown(
            """
        <style>
        .center-container { display: flex; flex-direction: column; align-items: center; }
        .youtube-input { width: 100%; padding: 10px; font-size: 16px; margin-bottom: 20px; }
        </style>
        """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="center-container">', unsafe_allow_html=True)
        self.youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="Paste YouTube URL here...",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if not os.getenv("GOOGLE_GEMINI_API_KEY"):
            st.warning(
                "⚠️ **Gemini API key is missing!** Please set it in the environment variables."
            )
            st.stop()

        if self.youtube_url:
            self.video_id = GetVideo.Id(self.youtube_url)
            if self.video_id is None:
                st.error("Invalid YouTube URL")
                st.stop()
            self.video_title = GetVideo.title(self.youtube_url)
            st.markdown(f"#### {self.video_title}", unsafe_allow_html=True)
            st.components.v1.iframe(f"https://www.youtube.com/embed/{self.video_id}", height=450)

    def generate_summary(self):
        with st.spinner("Generating Summary..."):
            try:
                self.video_transcript = GetVideo.transcript(self.youtube_url)
                if not self.video_transcript:
                    st.error("Transcript could not be retrieved. Please check the video URL.")
                    return

                self.summary = Model.google_gemini(self.video_transcript, Prompt.prompt1())
                
                if not self.summary or not isinstance(self.summary, str):
                    st.error("Failed to generate summary. Please try again later.")
                    return

                st.markdown("### Video Summary")
                st.write(self.summary)
                st_copy_to_clipboard(self.summary)  # Only called if `self.summary` is valid.
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


    def generate_time_stamps(self):
        with st.spinner("Generating Timestamps..."):
            self.video_transcript_time = GetVideo.transcript_time(self.youtube_url)
            self.time_stamps = Model.google_gemini(self.video_transcript_time, Prompt.prompt1(ID='timestamp'))
            st.markdown("### Video Timestamps")
            st.markdown(self.time_stamps)

    def generate_transcript(self):
        with st.spinner("Fetching Transcript..."):
            try:
                self.video_transcript = GetVideo.transcript(self.youtube_url)
                if not self.video_transcript:
                    st.error("Transcript could not be retrieved. Please check the video URL.")
                    return

                self.transcript = self.video_transcript

                # Fixed height for the text area with scroll bar
                st.markdown("### Video Transcript")
                st.text_area(
                    "Transcript",
                    self.transcript,
                    height=500,  # Set a fixed height
                    placeholder="Transcript will appear here...",
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


    def run(self):
        st.set_page_config(page_title="AI Video Summarizer", layout="wide")
        col1, col2 = st.columns([1, 14])  # The first column takes less space than the second

        with col1:
            st.image("https://em-content.zobj.net/content/2020/04/05/yt.png", width=60)  # Adjust width as needed

        with col2:
        # Custom HTML to increase the title font size
            st.markdown('<h1 style="font-size: 35px;">AI Video Summarizer</h1>', unsafe_allow_html=True)
        self.get_youtube_info()



        if self.youtube_url:
            mode = st.selectbox("What would you like to generate?", ["Summary", "Timestamps", "Transcript"])
            if mode == "Summary":
                self.generate_summary()
            elif mode == "Timestamps":
                self.generate_time_stamps()
            elif mode == "Transcript":
                self.generate_transcript()


if __name__ == "__main__":
    app = AIVideoSummarizer()
    app.run()
