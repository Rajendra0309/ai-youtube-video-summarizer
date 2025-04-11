import streamlit as st
import os
import sys
import importlib.util

# Set page config at the very beginning
st.set_page_config(
    page_title="AI Video Summarizer", 
    page_icon="🎥", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Check for required packages and handle the Google Generative AI dependency issue
def check_dependencies():
    missing_packages = []
    packages_to_check = [
        ("youtube_transcript_api", "youtube-transcript-api"),
        ("dotenv", "python-dotenv"),
        ("bs4", "beautifulsoup4"),
        ("requests", "requests")
    ]
    
    for module_name, package_name in packages_to_check:
        spec = importlib.util.find_spec(module_name.split('.')[0])
        if spec is None:
            missing_packages.append(package_name)
    
    # Special check for google.generativeai - silently handle it
    try:
        import google.generativeai
        # No success message here to avoid showing in UI
    except ImportError as e:
        if "google-generativeai" not in missing_packages:
            missing_packages.append("google-generativeai")
    except Exception as e:
        # Don't show any warning, just continue with fallback approach
        pass
    
    if missing_packages:
        st.error(f"⚠️ Missing required packages: {', '.join(missing_packages)}")
        st.code(f"pip install {' '.join(missing_packages)}")
        st.info("Please install the missing packages and restart the application.")
        return False
    return True

# Try to load the copy to clipboard package
try:
    from st_copy_to_clipboard import st_copy_to_clipboard
    has_clipboard = True
except ImportError:
    has_clipboard = False

# Now import the rest of our modules
from dotenv import load_dotenv
from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.timestamp_formatter import TimestampFormatter

# Run dependency check silently
if not check_dependencies():
    st.stop()

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
                "Please set the API key in your environment variables or .env file to use this application. "
                "You can obtain an API key from the [Google AI Studio](https://makersuite.google.com/app/apikey)."
            )
            if not self.youtube_url:
                st.stop()

        # Video Embedding with Enhanced Style
        if self.youtube_url:
            self.video_id = GetVideo.Id(self.youtube_url)
            if self.video_id is None:
                st.error("⚠️ Invalid YouTube URL. Please provide a valid YouTube video link.")
                st.stop()
            
            try:
                self.video_title = GetVideo.title(self.youtube_url)
                if self.video_title and self.video_title.startswith("⚠️"):
                    st.error(self.video_title)
                else:
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
            except Exception as e:
                st.error(f"⚠️ Error loading video: {str(e)}")

    def generate_summary(self):
        with st.spinner("🤖 AI is crafting a concise summary..."):
            try:
                self.video_transcript = GetVideo.transcript(self.youtube_url)
                if not self.video_transcript:
                    st.error("😔 Transcript could not be retrieved. This video may not have captions available.")
                    return

                self.summary = Model.google_gemini(self.video_transcript, Prompt.prompt1())
                
                if isinstance(self.summary, str) and self.summary.startswith("⚠️"):
                    st.error(self.summary)
                    return
                    
                st.markdown("### 📝 Video Summary")
                st.markdown(f'<div style="background-color: rgba(0,123,255,0.1); padding: 20px; border-radius: 10px;">{self.summary}</div>', unsafe_allow_html=True)
                
                if has_clipboard:
                    st_copy_to_clipboard(self.summary)
                else:
                    if st.button("📋 Copy Summary"):
                        # Provide alternative copy method for browsers
                        st.code(self.summary)
                        st.info("Select the text above and use Ctrl+C (or Cmd+C) to copy")
    
            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {str(e)}")

    def generate_time_stamps(self):
        with st.spinner("🕒 Generating Timestamps..."):
            try:
                self.video_transcript_time = GetVideo.transcript_time(self.youtube_url)
                if not self.video_transcript_time:
                    st.error("😔 Transcript with timestamps could not be retrieved. This video may not have captions available.")
                    return
                    
                raw_timestamps = Model.google_gemini(self.video_transcript_time, Prompt.prompt1(ID='timestamp'))
                
                if isinstance(raw_timestamps, str) and raw_timestamps.startswith("⚠️"):
                    st.error(raw_timestamps)
                    return
                
                # Format timestamps
                formatted_timestamps = TimestampFormatter.format(raw_timestamps)
                
                st.markdown("### 🕰️ Video Timestamps")
                st.markdown(
                    f'<div style="background-color: rgba(40,167,69,0.1); padding: 20px; border-radius: 10px; white-space: pre-wrap;">{formatted_timestamps}</div>', 
                    unsafe_allow_html=True
                )
                
                if has_clipboard:
                    st_copy_to_clipboard(formatted_timestamps)
                else:
                    if st.button("📋 Copy Timestamps"):
                        st.code(formatted_timestamps)
                        st.info("Select the text above and use Ctrl+C (or Cmd+C) to copy")
            
            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {str(e)}")

    def generate_transcript(self):
        with st.spinner("📝 Fetching Transcript..."):
            try:
                self.video_transcript = GetVideo.transcript(self.youtube_url)
                if not self.video_transcript:
                    st.error("😔 Transcript could not be retrieved. This video may not have captions available.")
                    return

                self.transcript = self.video_transcript

                # Fixed height for the text area with scroll bar
                st.markdown("### 📄 Video Transcript")
                st.text_area(
                    "Transcript",
                    self.transcript,
                    height=500,  # Set a fixed height
                    placeholder="Transcript will appear here...",
                    key="transcript_area"
                )
                
                if has_clipboard:
                    st_copy_to_clipboard(self.transcript)
                    
            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")

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