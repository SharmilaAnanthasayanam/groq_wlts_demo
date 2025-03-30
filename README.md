# Groq Whisper Large V3 - Word Level Timestamping Demo

This repository provides two applications that leverage the word-level timestamping functionality of the Whisper Large V3 model from Groq.

## Features

### 1. **Word Finder**
   - Jump directly to the specific part of a video without watching the entire content.
   - Provide a YouTube video URL and your Groq API key.
   - The video will be processed, and you can search for a word.
   - The exact timestamp where the word appears will be provided.

### 2. **Video Captioning**
   - Automatically generate captions for a YouTube video using word-level timestamping.
   - Provide the YouTube video URL, and captions will be added with precise timing.


## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/groq_wlts_demo.git
   cd groq_wlts_demo
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```
4. Enter the YouTube video URL and your Groq API key.
5. Use the Word Finder to search for specific words and their timestamps.
6. Use Video Captioning to generate and apply captions to the video.

## Acknowledgments
- Powered by Groq Whisper Large V3
- Built with Streamlit for an interactive UI

