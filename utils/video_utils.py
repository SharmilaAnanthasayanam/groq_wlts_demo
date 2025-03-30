import streamlit as st
import os
import tempfile
import subprocess
import yt_dlp

def download_youtube_video(youtube_url):
    """
    Download a YouTube video using yt-dlp and return the path to the downloaded file.
    """
    # Create a temporary directory to store the video
    temp_dir = tempfile.mkdtemp()

    # Set the output path for the video
    output_path = os.path.join(temp_dir, "video.mp4")

    # Use yt-dlp to download the video
    cmd = ["yt-dlp", "-f", "best[ext=mp4]", "-o", output_path, youtube_url]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        st.error(f"Error downloading video: {e.stderr.decode()}")
        return None

def format_timestamp(seconds):
    """
    Format seconds as HH:MM:SS,mmm for SRT files.
    """
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def generate_srt_from_whisper_json(transcription, output_path):
    """
    Generate an SRT file from Whisper JSON output.
    """
    segments = transcription.segments

    with open(output_path, "w") as srt_file:
        for i, segment in enumerate(segments):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()

            # Write SRT entry
            srt_file.write(f"{i+1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

    return output_path