import streamlit as st
from groq import Groq
import os
import re

def transcribe_audio_chunk(chunk_file, api_key):
    """Transcribe a single audio chunk using Groq API"""
    try:
        client = Groq(api_key=api_key)

        with open(chunk_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
                language="en",
                temperature=0.0,
            )

        return transcription
    except Exception as e:
        st.error(f"Error during chunk transcription: {e}")
        return None

def transcribe_audio(file_path, api_key, use_chunking=True):
    """
    Transcribe audio using Groq API with chunking for large files
    """
    try:
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        # If file is small enough or chunking is disabled, transcribe directly
        if file_size_mb < 30 or not use_chunking:  # 30MB is a safe limit for Groq API
            client = Groq(api_key=api_key)

            with open(file_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=file,
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                    timestamp_granularities=["word", "segment"],
                    language="en",
                    temperature=0.0,
                )

            return transcription

        # For larger files, use chunking
        else:
            from utils.audio_processing import chunk_audio

            st.info(f"Audio file is {file_size_mb:.1f}MB, using chunking for processing")

            # Split audio into chunks
            chunks = chunk_audio(file_path)

            if not chunks:
                return None

            # Process each chunk
            progress_bar = st.progress(0)
            status_text = st.empty()

            all_words = []
            all_segments = []

            for i, chunk_info in enumerate(chunks):
                chunk_file = chunk_info["file"]
                chunk_start_ms = chunk_info["start_ms"]

                # Update progress
                progress = (i) / len(chunks)
                progress_bar.progress(progress)
                status_text.text(f"Processing chunk {i+1}/{len(chunks)}")

                # Transcribe chunk
                chunk_result = transcribe_audio_chunk(chunk_file, api_key)

                if chunk_result:
                    # Adjust timestamps based on chunk position
                    chunk_start_seconds = chunk_start_ms / 1000

                    # Process words
                    if hasattr(chunk_result, "words"):
                        for word in chunk_result.words:
                            # Adjust timestamps
                            word_start = word.get("start") + chunk_start_seconds
                            word_end = word.get("end") + chunk_start_seconds

                            all_words.append({"word": word.get("word"), "start": word_start, "end": word_end})

                    # Process segments
                    if hasattr(chunk_result, "segments"):
                        for segment in chunk_result.segments:
                            # Adjust timestamps
                            segment_start = segment.get("start") + chunk_start_seconds
                            segment_end = segment.get("end") + chunk_start_seconds

                            all_segments.append(
                                {
                                    "id": segment.get("id"),
                                    "seek": segment.get("seek"),
                                    "start": segment_start,
                                    "end": segment_end,
                                    "text": segment.get("text"),
                                    "tokens": segment.get("tokens"),
                                    "temperature": segment.get("temperature"),
                                    "avg_logprob": segment.get("avg_logprob"),
                                    "compression_ratio": segment.get("compression_ratio"),
                                    "no_speech_prob": segment.get("no_speech_prob"),
                                }
                            )

                # Clean up chunk file
                try:
                    os.unlink(chunk_file)
                except:
                    pass

            # Update progress to complete
            progress_bar.progress(1.0)
            status_text.text("Processing complete!")

            # Create a combined result object
            class CombinedTranscription:
                def __init__(self, words, segments, text):
                    self.words = words
                    self.segments = segments
                    self.text = text

            # Combine all segment texts
            full_text = " ".join([segment["text"] for segment in all_segments])

            # Create the combined result
            combined_result = CombinedTranscription(all_words, all_segments, full_text)

            return combined_result

    except Exception as e:
        st.error(f"Error during transcription: {e}")
        return None

def find_word_instances(transcription, search_word):
    """Find instances of a word in the transcription"""
    if not hasattr(transcription, "words") or not transcription.words:
        return []

    # Case-insensitive search
    pattern = re.compile(r"\b" + re.escape(search_word) + r"\b", re.IGNORECASE)

    found_instances = []
    for word_info in transcription.words:
        word = word_info.get("word")
        if pattern.search(word):
            found_instances.append({
                "word": word,
                "start": word_info.get("start"),
                "end": word_info.get("end")
            })

    return found_instances