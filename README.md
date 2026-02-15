# 🎥 AI YouTube Video Summarizer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-ff4b4b)
![Gemini AI](https://img.shields.io/badge/Google-Gemini%20AI-4285F4)
![License](https://img.shields.io/badge/License-MIT-green)

Transform long YouTube videos into concise summaries, detailed timestamps, and accurate transcripts in seconds. Powered by Google's Gemini AI, this tool supports over 30 languages and features a premium, responsive UI.

---

## ✨ Key Features

- **📝 Smart Summaries**: Get concise, bullet-point summaries of any YouTube video.
- **🕒 Automatic Timestamps**: Generate chapter-like timestamps to navigate key topics easily.
- **📄 Full Transcripts**: Extract accurate transcripts even if the video doesn't have captions (AI-generated fallback).
- **🌍 Multi-Language Support**: Summarize and transcribe content in **34+ languages** (English, Hindi, Spanish, French, German, and many more).
- **🌗 Dark & Light Mode**: A beautifully crafted UI with a toggle switch for comfortable viewing in any lighting.
- **📱 Fully Responsive**: Works perfectly on desktops, tablets, and mobile devices.
- **⚡ High Performance**: Fast processing using optimized Gemini 2.0 Flash models.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (Python-based web framework)
- **AI Model**: [Google Gemini 2.5 Flash / 2.0 Flash](https://ai.google.dev/) (Text & Video capabilities)
- **Backend Logic**: Python
- **APIs & Libraries**: 
  - `google-generativeai`
  - `youtube-transcript-api`
  - `beautifulsoup4` (Web scraping fallback)
  - `yt-dlp` (Advanced video data extraction)

## 🚀 Installation & Setup

Follow these steps to run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-youtube-video-summarizer.git
cd ai-youtube-video-summarizer
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up API Key
1. Get your free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Create a `.env` file by copying the example:
```bash
cp .env.example .env
# Windows: copy .env.example .env
```
3. Open `.env` and paste your API key:
```env
GOOGLE_GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run the Application
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`.

## 📖 Usage Guide

1. **Paste URL**: Copy any YouTube video link and paste it into the input field.
2. **Select Mode**: Choose between **Summary**, **Timestamps**, or **Transcript**.
3. **Choose Language**: Pick your preferred output language (e.g., English, Hindi, Spanish) or let it **Auto-Detect**.
4. **View Results**: The AI will process the video and display the results in formatted cards. You can copy the text with one click!

## � Project Structure

```
ai-youtube-video-summarizer/
├── src/
│   ├── model.py          # Gemini AI model integration
│   ├── prompt.py         # Prompt engineering templates
│   ├── video_info.py     # YouTube transcript & metadata extraction
│   └── timestamp_formatter.py # Formatting logic for timestamps
├── app.py                # Main Streamlit application
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API Key)
└── README.md             # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.