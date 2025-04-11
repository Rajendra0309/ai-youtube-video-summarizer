<h1 align="center">
  <br>
  <img src="https://www.freepnglogos.com/uploads/youtube-circle-icon-png-logo-14.png" alt="AI YouTube Video Summarizer" width="200">
  <br>
   🎥 AI Video Summarization & Timestamp Generator
  <br>
</h1>

<h4 align="center">Harnessing the Power of LLMs for Enhanced Video Understanding</h4>

<p align="center">
  <a href="#overview-">Overview</a> •
  <a href="#features-">Features</a> •
  <a href="#getting-started-">Getting Started</a> •
  <a href="#contributing">Contributing</a> 
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com//main/research/demo3.gif" alt="Usage Demo">
</p>

## Overview 📝

This project is an AI-powered video summarizer designed specifically for YouTube videos. Leveraging the Google Gemini API, it employs advanced machine learning techniques to analyze and condense lengthy YouTube videos into concise summaries, providing users with quick insights into the video content.

## Features ✨

- Automatic extraction of key insights and timestamps from YouTube videos.
- Utilizes youtube-transcript-api for getting the transcripts/subtitles YouTube video.
- Option for users to select AI models like *ChatGPT* or *Gemini* for summarization.
- Efficiently summarizes videos, reducing viewing time while preserving essential information.

## Getting Started 🚀

### Prerequisites

- Python 3.10
- LLM Model API Keys [[🔑]](#get-api-keys)

### Usage

1. Clone the repository:
git clone https://github.com/Rajendra0309/ai-youtube-video-summarizer.git
2. Navigate to the project directory:
cd ai-youtube-video-summarizer
3. Install dependencies:
pip install -r requirements.txt
4. Create a ".env" file ⬇️ [add whichever is available]
GOOGLE_GEMINI_API_KEY = "Your-Gemini-Key-Here"

### Get API Key:

- [Google Gemini API key](https://makersuite.google.com/app/apikey) 🔑 
   
5. Run the summarizer:
streamlit run app.py

## Contributing

Contributions are welcome from the community! Whether it's feedback, suggestions, or code improvements, your input is valuable. 

## Acknowledgments

- [Google Gemini](https://ai.google.dev/)
