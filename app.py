import streamlit as st
import os
import json
import re

# Import utility modules
from utils.audio_processing import download_youtube_audio, get_audio_player_html
from utils.transcription import transcribe_audio, find_word_instances
from utils.video_utils import download_youtube_video, generate_srt_from_whisper_json
from utils.ui_components import apply_custom_css, display_app_header, create_styled_container, display_footer, display_word_search_results, display_badge

# Page configuration with custom title and icon
st.set_page_config(page_title="Groq Whisper WLTS Demo", page_icon="🎵", layout="wide")

# Apply custom CSS
apply_custom_css()

# Display app header
display_app_header()

# Display badge
display_badge()

# Create tabs
tab1, tab2 = st.tabs(["Word Finder", "Video Captioning"])

with tab1:
    # Define the content function for the Word Finder container
    def word_finder_content():
        # Input for API key
        api_key = st.text_input("Enter your Groq API Key", type="password")

        # YouTube URL input
        youtube_url = st.text_input("Enter YouTube URL")

        # Process button
        if st.button("Process Video"):
            if not api_key:
                st.error("Please enter your Groq API Key")
            elif not youtube_url:
                st.error("Please enter a YouTube URL")
            else:
                # Create a progress bar
                progress_bar = st.progress(0)

                # Use status for better visual feedback
                with st.status("Processing your video...", expanded=True) as status:
                    st.write("Downloading audio...")
                    progress_bar.progress(25)

                    audio_file, video_title = download_youtube_audio(youtube_url)

                    if audio_file:
                        st.write(f"Downloaded audio from: {video_title}")
                        progress_bar.progress(50)

                        # Display audio player
                        st.subheader("Audio")
                        audio_html = get_audio_player_html(audio_file)
                        st.markdown(audio_html, unsafe_allow_html=True)

                        # Transcribe
                        st.write("Transcribing audio...")
                        progress_bar.progress(75)

                        transcription = transcribe_audio(audio_file, api_key)

                        if transcription:
                            progress_bar.progress(100)
                            status.update(label="Processing complete!", state="complete")

                            # Store in session state
                            st.session_state.transcription = transcription
                            st.session_state.audio_file = audio_file
                            st.session_state.video_title = video_title

                            # Show success message
                            st.success("Transcription complete! Now you can search for words.")

        # Word search section (only show if transcription exists)
        if "transcription" in st.session_state:

            st.subheader("Find Words")
            search_word = st.text_input("Enter word or phrase to search")

            if search_word and st.button("Find"):
                transcription = st.session_state.transcription

                # Find instances of the word
                found_instances = find_word_instances(transcription, search_word)

                # Display results
                display_word_search_results(
                    found_instances,
                    st.session_state.audio_file if "audio_file" in st.session_state else None,
                    st.session_state.transcription if "transcription" in st.session_state else None,
                )

    # Create the styled container for Word Finder
    create_styled_container(
        key="word_finder_input",
        content_function=word_finder_content,
        title="Find specific words in YouTube videos",
        description="Enter a YouTube URL and search for specific words to get their timestamps"
    )

with tab2:
    # Define the content function for the Video Captioning container
    def video_captioning_content():
        # Add unique keys to all inputs
        api_key_captioning = st.text_input("Enter your Groq API Key", type="password", key="captioning_api_key")
        youtube_url_captioning = st.text_input("Enter YouTube URL", key="captioning_youtube_url")

        if st.button("Generate Captions", key="generate_captions_btn"):
            if not youtube_url_captioning:
                st.error("Please enter a YouTube URL")
            else:
                with st.status("Processing video..."):
                    # Download video
                    st.write("Downloading video...")
                    video_path = download_youtube_video(youtube_url_captioning)

                    if not video_path:
                        st.error("Failed to download video")
                    else:
                        # Extract audio
                        st.write("Extracting audio...")
                        from utils.audio_processing import extract_audio

                        audio_path = extract_audio(video_path)

                        if not audio_path:
                            st.error("Failed to extract audio")
                        else:
                            # Transcribe with Whisper
                            st.write("Transcribing audio...")
                            transcription = transcribe_audio(audio_path, api_key_captioning, use_chunking=True)

                            # Generate SRT file
                            st.write("Generating captions...")
                            os.makedirs("output", exist_ok=True)
                            srt_path = "output/captions.srt"
                            generate_srt_from_whisper_json(transcription, srt_path)

                            # Save paths to session state
                            st.session_state.video_path = video_path
                            st.session_state.srt_path = srt_path

                # Display video with captions
                if hasattr(st.session_state, "video_path") and hasattr(st.session_state, "srt_path"):
                    # Read the SRT file content
                    with open(st.session_state.srt_path, "r") as f:
                        srt_content = f.read()

                    # Display video with subtitles
                    st.video(st.session_state.video_path, subtitles=srt_content)

                    # Offer download of SRT file
                    st.download_button("Download SRT file", srt_content, "captions.srt", key="download_srt")

    # Create the styled container for Video Captioning
    create_styled_container(
        key="video_caption_input",
        content_function=video_captioning_content,
        title="Generate and Add Captions to Videos",
        description="Create accurate captions for your videos using Groq's whisper-large-v3-turbo model"
    )

# Display footer
display_footer()
