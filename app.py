import streamlit as st
import os
import importlib.util
import traceback
from urllib.parse import urlparse

st.set_page_config(
    page_title="AI Video Summarizer",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

    if missing_packages:
        st.error(f"⚠️ Missing required packages: {', '.join(missing_packages)}")
        st.code(f"pip install {' '.join(missing_packages)}")
        st.info("Please install the missing packages and restart the application.")
        return False
    return True

try:
    from st_copy_to_clipboard import st_copy_to_clipboard
    has_clipboard = True
except ImportError:
    has_clipboard = False

from dotenv import load_dotenv
from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.timestamp_formatter import TimestampFormatter

if not check_dependencies():
    st.stop()

LANGUAGE_OPTIONS = {
    "Auto-Detect": "auto",
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Bengali (বাংলা)": "bn",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Marathi (मराठी)": "mr",
    "Gujarati (ગુજરાતી)": "gu",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Odia (ଓଡ଼ିଆ)": "or",
    "Urdu (اردو)": "ur",
    "Assamese (অসমীয়া)": "as",
    "Nepali (नेपाली)": "ne",
    "Sinhala (සිංහල)": "si",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "German (Deutsch)": "de",
    "Portuguese (Português)": "pt",
    "Italian (Italiano)": "it",
    "Russian (Русский)": "ru",
    "Japanese (日本語)": "ja",
    "Korean (한국어)": "ko",
    "Chinese (中文)": "zh",
    "Arabic (العربية)": "ar",
    "Turkish (Türkçe)": "tr",
    "Dutch (Nederlands)": "nl",
    "Polish (Polski)": "pl",
    "Vietnamese (Tiếng Việt)": "vi",
    "Thai (ไทย)": "th",
    "Indonesian (Bahasa)": "id",
    "Swedish (Svenska)": "sv",
    "Filipino (Tagalog)": "fil",
}


def format_transcript(raw_text):
    """Clean and format raw transcript text into readable paragraphs."""
    import re
    text = raw_text

    # Replace >> speaker markers with newlines
    text = re.sub(r'\s*>>\s*', '\n\n', text)

    # Clean up multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Clean up excessive newlines (3+ becomes 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Trim each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, *::before, *::after { box-sizing: border-box; }
* { font-family: 'Inter', sans-serif; }

.app-header { text-align: center; padding: 1.5rem 0 0.5rem; }
.app-header h1 {
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}
.app-header p {
    font-size: 1.05rem;
    margin-top: 0.3rem;
    font-weight: 300;
}

.video-title {
    text-align: center;
    font-size: 1.3rem;
    font-weight: 600;
    margin: 0.6rem 0;
    line-height: 1.4;
}

.video-embed-wrapper {
    display: flex;
    justify-content: center;
    margin: 1rem auto;
    padding: 0 1rem;
    max-width: 720px;
    width: 100%;
}
.video-embed-frame {
    border-radius: 16px;
    overflow: hidden;
    width: 100%;
    position: relative;
    aspect-ratio: 16 / 9;
}
.video-embed-frame iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 0;
}

.result-card {
    border-radius: 16px;
    padding: 1.8rem;
    margin-top: 1rem;
    animation: fadeInUp 0.5s ease;
}
.result-card.summary-card { border-left: 4px solid #667eea; }
.result-card.timestamp-card { border-left: 4px solid #48bb78; }
.result-card.transcript-card { border-left: 4px solid #ed8936; }

.result-header {
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.result-content { line-height: 1.8; font-size: 0.95rem; }

.hero-section { text-align: center; padding: 2.5rem 1rem; animation: fadeInUp 0.6s ease; }
.feature-grid {
    display: flex;
    justify-content: center;
    gap: 1.2rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
}
.feature-item {
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    width: 195px;
    transition: all 0.3s ease;
}
.feature-item:hover { transform: translateY(-4px); }
.feature-icon { font-size: 2rem; margin-bottom: 0.4rem; }
.feature-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 0.3rem; }
.feature-desc { font-size: 0.78rem; line-height: 1.4; }

.input-section { max-width: 700px; margin: 0 auto; padding: 0 1rem; width: 100%; }
.input-label {
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.divider { height: 1px; margin: 1.2rem 0; }

.footer { text-align: center; padding: 2rem 0 1rem; font-size: 0.8rem; }
.footer a { text-decoration: none; }

.theme-toggle-btn {
    position: fixed;
    top: 0.8rem;
    right: 1rem;
    z-index: 999;
    cursor: pointer;
    font-size: 1.5rem;
    background: none;
    border: none;
    padding: 0.3rem;
    transition: transform 0.3s ease;
}
.theme-toggle-btn:hover { transform: scale(1.15); }

div[data-testid="stStatusWidget"] { display: none; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Tablet (<=1024px) */
@media (max-width: 1024px) {
    .app-header h1 { font-size: 2.2rem; }
    .app-header p { font-size: 0.95rem; }
    .feature-item { width: 170px; padding: 1rem 1.2rem; }
    .video-embed-wrapper { max-width: 600px; }
    .result-card { padding: 1.4rem; }
}

/* Mobile landscape / small tablet (<=768px) */
@media (max-width: 768px) {
    .app-header { padding: 1rem 0 0.3rem; }
    .app-header h1 { font-size: 1.8rem; }
    .app-header p { font-size: 0.88rem; }
    .video-title { font-size: 1.1rem; }
    .feature-grid { gap: 0.8rem; }
    .feature-item { width: 42%; min-width: 140px; padding: 1rem; }
    .feature-icon { font-size: 1.6rem; }
    .feature-title { font-size: 0.85rem; }
    .feature-desc { font-size: 0.72rem; }
    .hero-section { padding: 1.5rem 0.5rem; }
    .result-card { padding: 1.2rem; border-radius: 12px; }
    .result-header { font-size: 1.05rem; }
    .result-content { font-size: 0.88rem; line-height: 1.7; }
    .input-label { font-size: 0.8rem; }
    .divider { margin: 0.8rem 0; }
}

/* Mobile portrait (<=480px) */
@media (max-width: 480px) {
    .app-header { padding: 0.8rem 0 0.2rem; }
    .app-header h1 { font-size: 1.5rem; letter-spacing: -0.3px; }
    .app-header p { font-size: 0.8rem; }
    .video-title { font-size: 1rem; margin: 0.4rem 0; }
    .video-embed-wrapper { padding: 0 0.5rem; margin: 0.5rem auto; }
    .video-embed-frame { border-radius: 10px; }
    .feature-grid { gap: 0.6rem; margin-top: 1rem; }
    .feature-item { width: 100%; max-width: 280px; padding: 0.9rem 1rem; }
    .hero-section { padding: 1rem 0.5rem; }
    .input-section { padding: 0 0.5rem; }
    .result-card { padding: 1rem; margin-top: 0.8rem; border-radius: 10px; }
    .result-header { font-size: 1rem; margin-bottom: 0.7rem; }
    .result-content { font-size: 0.85rem; line-height: 1.6; }
    .theme-toggle-btn { font-size: 1.2rem; top: 0.5rem; right: 0.5rem; }
}
"""

DARK_CSS = """
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: #e0e0e0;
}
.app-header h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.app-header p { color: #8b8fa3; }
.video-title { color: #c4b5fd; }
.video-embed-frame {
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.result-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(16px);
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    border-right: 1px solid rgba(255, 255, 255, 0.06);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.result-header.summary { color: #818cf8; }
.result-header.timestamp { color: #68d391; }
.result-header.transcript { color: #f6ad55; }
.result-content { color: #d1d5db; }

.feature-item {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.feature-item:hover {
    border-color: rgba(102, 126, 234, 0.3);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
}
.feature-title { color: #c4b5fd; }
.feature-desc { color: #6b7280; }

.input-label { color: #8b8fa3; }
.divider { background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent); }
.footer { color: #4a5568; }
.footer a { color: #667eea; }

.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
    padding: 0.8rem 1.2rem !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.25) !important;
}
.stTextInput > div > div > input::placeholder { color: #6b7280 !important; }

.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
}
.stSelectbox [data-baseweb="select"] span { color: #e0e0e0 !important; }

.stRadio > div > label {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.2rem !important;
    color: #a5b4fc !important;
}

.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    color: #f0f0f0 !important;
    line-height: 1.7 !important;
    font-size: 0.92rem !important;
}
.stTextArea textarea { color: #f0f0f0 !important; }
[data-testid="stTextArea"] textarea { color: #f0f0f0 !important; }
.stTextArea label { color: #e0e0e0 !important; }

.stSpinner > div { color: #a5b4fc !important; }

.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
}

[data-testid="stAlert"] {
    background: rgba(237, 137, 54, 0.08) !important;
    border: 1px solid rgba(237, 137, 54, 0.2) !important;
    border-radius: 12px !important;
}
"""

LIGHT_CSS = """
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 50%, #f0f4f8 100%);
    color: #1a202c;
}
.app-header h1 {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #c026d3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.app-header p { color: #64748b; }
.video-title { color: #4f46e5; }
.video-embed-frame {
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
    border: 1px solid rgba(0, 0, 0, 0.06);
}
.result-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(16px);
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    border-right: 1px solid rgba(0, 0, 0, 0.06);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}
.result-header.summary { color: #4f46e5; }
.result-header.timestamp { color: #059669; }
.result-header.transcript { color: #d97706; }
.result-content { color: #374151; }

.feature-item {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.feature-item:hover {
    border-color: rgba(79, 70, 229, 0.3);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}
.feature-title { color: #4f46e5; }
.feature-desc { color: #64748b; }

.input-label { color: #64748b; }
.divider { background: linear-gradient(90deg, transparent, rgba(79, 70, 229, 0.2), transparent); }
.footer { color: #94a3b8; }
.footer a { color: #4f46e5; }

.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    color: #1a202c !important;
    padding: 0.8rem 1.2rem !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2) !important;
}
.stTextInput > div > div > input::placeholder { color: #9ca3af !important; }

.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    color: #1a202c !important;
}
.stSelectbox [data-baseweb="select"] span { color: #1a202c !important; }

.stRadio > div > label {
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.2rem !important;
    color: #4f46e5 !important;
}

.stTextArea > div > div > textarea {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    color: #1a202c !important;
    line-height: 1.7 !important;
    font-size: 0.92rem !important;
}
.stTextArea textarea { color: #1a202c !important; background: #ffffff !important; }
[data-testid="stTextArea"] textarea { color: #1a202c !important; }
.stTextArea label { color: #374151 !important; }

.stSpinner > div { color: #4f46e5 !important; }

.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.3) !important;
}

[data-testid="stAlert"] {
    background: rgba(245, 158, 11, 0.08) !important;
    border: 1px solid rgba(245, 158, 11, 0.2) !important;
    border-radius: 12px !important;
}

p, span, li, td, th, label, .stMarkdown { color: #1a202c !important; }
h1, h2, h3, h4, h5, h6 { color: #1e293b !important; }
.app-header h1 { -webkit-text-fill-color: transparent !important; }
.app-header p { color: #64748b !important; }
.video-title { color: #4f46e5 !important; }
.result-header.summary { color: #4f46e5 !important; }
.result-header.timestamp { color: #059669 !important; }
.result-header.transcript { color: #d97706 !important; }
.result-content { color: #374151 !important; }
.feature-title { color: #4f46e5 !important; }
.feature-desc { color: #64748b !important; }
.input-label { color: #64748b !important; }
.footer { color: #94a3b8 !important; }
"""


def inject_css(theme):
    theme_css = DARK_CSS if theme == "dark" else LIGHT_CSS
    st.markdown(f"<style>{SHARED_CSS}\n{theme_css}</style>", unsafe_allow_html=True)


class AIVideoSummarizer:
    def __init__(self):
        if 'selected_language' not in st.session_state:
            st.session_state.selected_language = 'Auto-Detect'
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
        load_dotenv()

    def _render_header(self):
        theme = st.session_state.theme
        toggle_icon = "☀️" if theme == "dark" else "🌙"

        col1, col2 = st.columns([11, 1])
        with col2:
            if st.button(toggle_icon, key="theme_toggle", help="Toggle dark/light mode"):
                st.session_state.theme = "light" if theme == "dark" else "dark"
                st.rerun()

        st.markdown("""
        <div class="app-header">
            <h1>🎥 AI Video Summarizer</h1>
            <p>Extract summaries, timestamps, and transcripts from any YouTube video</p>
        </div>
        """, unsafe_allow_html=True)

    def _render_hero(self):
        st.markdown("""
        <div class="hero-section">
            <div class="feature-grid">
                <div class="feature-item">
                    <div class="feature-icon">📝</div>
                    <div class="feature-title">Smart Summary</div>
                    <div class="feature-desc">AI-powered concise summaries with key insights</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🕐</div>
                    <div class="feature-title">Timestamps</div>
                    <div class="feature-desc">Auto-generated chapter timestamps for navigation</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">📄</div>
                    <div class="feature-title">Transcripts</div>
                    <div class="feature-desc">Full video transcript in your preferred language</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🌐</div>
                    <div class="feature-title">34+ Languages</div>
                    <div class="feature-desc">Support for Indian, European, Asian & more</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def get_youtube_info(self):
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown('<p class="input-label">🔗 Paste YouTube URL</p>', unsafe_allow_html=True)
        self.youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="youtube_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if not os.getenv("GOOGLE_GEMINI_API_KEY"):
            st.warning(
                "⚠️ **Gemini API key is missing!**  \n"
                "Add your API key to the `.env` file. "
                "Get one from [Google AI Studio](https://aistudio.google.com/apikey)."
            )
            if not self.youtube_url:
                st.stop()

        if self.youtube_url:
            try:
                self.video_id = GetVideo.Id(self.youtube_url)
                if self.video_id is None:
                    st.error("⚠️ Invalid YouTube URL. Please provide a valid YouTube video link.")
                    st.stop()

                parsed_url = urlparse(self.youtube_url)
                if not parsed_url.scheme:
                    self.youtube_url = f"https://www.youtube.com/watch?v={self.video_id}"

                self.video_title = GetVideo.title(self.youtube_url)

                if not self.video_title or (isinstance(self.video_title, str) and self.video_title.startswith("⚠️")):
                    self.video_title = f"YouTube Video ({self.video_id})"

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown(f'<p class="video-title">{self.video_title}</p>', unsafe_allow_html=True)

                embed_url = f"https://www.youtube.com/embed/{self.video_id}"
                st.markdown(
                    f'<div class="video-embed-wrapper">'
                    f'<div class="video-embed-frame">'
                    f'<iframe src="{embed_url}" '
                    f'allowfullscreen></iframe>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"⚠️ Error loading video: {str(e)}")
                print(f"Error details: {traceback.format_exc()}")

    def _get_language_code(self):
        return LANGUAGE_OPTIONS.get(st.session_state.selected_language, "auto")

    def _get_language_name(self):
        lang = st.session_state.selected_language
        if lang == "Auto-Detect":
            return "the same language as the video"
        return lang.split(" (")[0]

    def get_transcript(self):
        if not self.youtube_url or not self.video_id:
            return None

        lang_code = self._get_language_code()
        preferred = lang_code if lang_code != "auto" else None

        for attempt in range(2):
            try:
                transcript = GetVideo.transcript(self.youtube_url, preferred_lang=preferred)
                if transcript:
                    return transcript
            except:
                pass

        return None

    def get_transcript_time(self):
        if not self.youtube_url or not self.video_id:
            return None

        lang_code = self._get_language_code()
        preferred = lang_code if lang_code != "auto" else None

        for attempt in range(2):
            try:
                transcript = GetVideo.transcript_time(self.youtube_url, preferred_lang=preferred)
                if transcript:
                    return transcript
            except:
                pass

        return None

    def generate_summary(self):
        with st.spinner("🤖 AI is crafting a concise summary..."):
            try:
                language = self._get_language_name()
                prompt = Prompt.prompt1(language=language)
                result = None

                # Try transcript-based approach first (faster & more complete)
                self.video_transcript = self.get_transcript()
                if self.video_transcript:
                    result = Model.google_gemini(self.video_transcript, prompt)

                # Fall back to video API if no transcript
                if not result or (isinstance(result, str) and result.startswith("⚠️")):
                    video_url = f"https://www.youtube.com/watch?v={self.video_id}"
                    video_result = Model.google_gemini_video(video_url, prompt)
                    if video_result and not (isinstance(video_result, str) and video_result.startswith("⚠️")):
                        result = video_result

                if not result:
                    st.error("😔 Could not generate summary. Please check your Gemini API key and try again.")
                    return

                if isinstance(result, str) and result.startswith("⚠️"):
                    st.error(result)
                    return

                self.summary = result
                st.markdown(f"""
                <div class="result-card summary-card">
                    <div class="result-header summary">📝 Video Summary</div>
                    <div class="result-content">{self.summary}</div>
                </div>
                """, unsafe_allow_html=True)

                if has_clipboard:
                    st_copy_to_clipboard(self.summary)
                else:
                    if st.button("📋 Copy Summary"):
                        st.code(self.summary)

            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {str(e)}")
                print(f"Error details: {traceback.format_exc()}")

    def generate_time_stamps(self):
        with st.spinner("🕒 Generating timestamps..."):
            try:
                language = self._get_language_name()
                timestamp_prompt = Prompt.prompt1(ID='timestamp', language=language)
                result = None

                # Try transcript-based approach first (faster & has full content)
                self.video_transcript_time = self.get_transcript_time()
                if self.video_transcript_time:
                    result = Model.google_gemini(self.video_transcript_time, timestamp_prompt)

                # Fall back to video API if no transcript
                if not result or (isinstance(result, str) and result.startswith("⚠️")):
                    video_url = f"https://www.youtube.com/watch?v={self.video_id}"
                    video_result = Model.google_gemini_video(video_url, timestamp_prompt)
                    if video_result and not (isinstance(video_result, str) and video_result.startswith("⚠️")):
                        result = video_result

                if not result:
                    st.error("😔 Could not generate timestamps. Please check your Gemini API key and try again.")
                    return

                if isinstance(result, str) and result.startswith("⚠️"):
                    st.error(result)
                    return

                formatted_timestamps = TimestampFormatter.format(result)

                st.markdown(f"""
                <div class="result-card timestamp-card">
                    <div class="result-header timestamp">🕰️ Video Timestamps</div>
                    <div class="result-content" style="white-space: pre-wrap;">{formatted_timestamps}</div>
                </div>
                """, unsafe_allow_html=True)

                if has_clipboard:
                    st_copy_to_clipboard(formatted_timestamps)
                else:
                    if st.button("📋 Copy Timestamps"):
                        st.code(formatted_timestamps)

            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {str(e)}")
                print(f"Error details: {traceback.format_exc()}")

    def generate_transcript(self):
        with st.spinner("📝 Fetching transcript..."):
            try:
                language = self._get_language_name()
                self.video_transcript = self.get_transcript()

                if not self.video_transcript:
                    video_url = f"https://www.youtube.com/watch?v={self.video_id}"
                    gemini_transcript = Model.google_gemini_video(
                        video_url,
                        f"Provide a complete word-for-word transcript of this video in {language}. Do not add any commentary, headings, or formatting. Just output the spoken words exactly as they appear in the video."
                    )
                    if gemini_transcript:
                        self.video_transcript = gemini_transcript

                if not self.video_transcript:
                    st.error("😔 Could not retrieve transcript. Please check your Gemini API key and try again.")
                    return

                self.transcript = format_transcript(self.video_transcript)

                st.markdown("""
                <div class="result-card transcript-card">
                    <div class="result-header transcript">📄 Video Transcript</div>
                </div>
                """, unsafe_allow_html=True)

                st.text_area(
                    "Transcript",
                    self.transcript,
                    height=450,
                    placeholder="Transcript will appear here...",
                    key="transcript_area",
                    label_visibility="collapsed"
                )

                if has_clipboard:
                    st_copy_to_clipboard(self.transcript)
                else:
                    if st.button("📋 Copy Transcript"):
                        st.code(self.transcript)

            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")
                print(f"Error details: {traceback.format_exc()}")

    def run(self):
        st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">', unsafe_allow_html=True)
        inject_css(st.session_state.theme)
        self._render_header()
        self.get_youtube_info()

        if not self.youtube_url:
            self._render_hero()

        if self.youtube_url and self.video_id:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            col_mode, col_lang = st.columns([2.5, 1])

            with col_mode:
                mode = st.radio(
                    "Mode",
                    ["Summary", "Timestamps", "Transcript"],
                    horizontal=True,
                    label_visibility="collapsed"
                )

            with col_lang:
                st.session_state.selected_language = st.selectbox(
                    "🌐 Language",
                    list(LANGUAGE_OPTIONS.keys()),
                    index=list(LANGUAGE_OPTIONS.keys()).index(st.session_state.selected_language),
                    label_visibility="collapsed"
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