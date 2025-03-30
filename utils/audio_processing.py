import os
import tempfile
import numpy as np
from pydub import AudioSegment
import streamlit as st
import base64
import yt_dlp
import subprocess

def chunk_audio(audio_file, chunk_size_mb=30, overlap_seconds=2):
    """
    Split audio file into chunks with overlap
    """
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_file)

        # Calculate chunk size in milliseconds
        bytes_per_second = 16000 * 2  # 16kHz * 16-bit (2 bytes)
        seconds_per_mb = 1024 * 1024 / bytes_per_second
        chunk_size_ms = int(chunk_size_mb * seconds_per_mb * 1000)

        # Calculate overlap in milliseconds
        overlap_ms = overlap_seconds * 1000

        # Calculate number of chunks
        audio_length_ms = len(audio)
        effective_chunk_size = chunk_size_ms - overlap_ms
        num_chunks = max(1, int(np.ceil(audio_length_ms / effective_chunk_size)))

        st.info(f"Splitting audio into {num_chunks} chunks for processing")

        # Create chunks with overlap
        chunk_files = []
        for i in range(num_chunks):
            start_ms = i * effective_chunk_size
            end_ms = min(start_ms + chunk_size_ms, audio_length_ms)

            # Extract chunk
            chunk = audio[start_ms:end_ms]

            # Save chunk to temporary file
            chunk_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            chunk.export(chunk_file.name, format="mp3")
            chunk_files.append({"file": chunk_file.name, "start_ms": start_ms, "end_ms": end_ms})

        return chunk_files

    except Exception as e:
        st.error(f"Error chunking audio: {e}")
        return None

def get_audio_player_html(audio_path):
    """Create an HTML audio player for the given audio file"""
    audio_format = audio_path.split(".")[-1].lower()

    # Read audio file and encode to base64
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()

    # Create HTML audio player
    audio_html = f"""
    <audio controls style="width: 100%;">
        <source src="data:audio/{audio_format};base64,{audio_b64}" type="audio/{audio_format}">
        Your browser does not support the audio element.
    </audio>
    """
    return audio_html

def download_youtube_audio(youtube_url):
    """Download audio from YouTube video using yt-dlp"""
    try:
        # Create a temporary directory to store the downloaded file
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, "audio.%(ext)s")

        # Configure yt-dlp to download audio only
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [],
            "keepvideo": False,
        }

        # Download the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info.get("title", "YouTube Video")

            # Find the downloaded file
            downloaded_files = os.listdir(temp_dir)
            if not downloaded_files:
                st.error("No files were downloaded")
                return None, None

            downloaded_file = os.path.join(temp_dir, downloaded_files[0])

            # Return the file path and title
            return downloaded_file, title

    except Exception as e:
        st.error(f"Error downloading YouTube audio: {e}")
        return None, None

def extract_audio(video_path):
    """
    Extract audio from a video file using FFmpeg.
    """
    # Create output path for audio
    audio_path = os.path.splitext(video_path)[0] + ".mp3"

    # Use FFmpeg to extract audio
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        "-y",  # Overwrite output file if it exists
        audio_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return audio_path
    except subprocess.CalledProcessError as e:
        st.error(f"Error extracting audio: {e.stderr.decode()}")
        return None