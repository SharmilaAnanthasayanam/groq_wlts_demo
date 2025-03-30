import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils.audio_processing import get_audio_player_html
import base64
import os


def apply_custom_css():
    """Apply custom CSS styling to the entire application."""
    # Hide default menu and footer
    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Reduce top padding of the main container */
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }

        /* Main header styling */
        .main-header {
            background-color: #4B89DC;
            padding: 1.2rem;
            border-radius: 0.5rem;
            color: white;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;  /* Increase gap between tabs */
            margin-bottom: 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 60px !important;  /* Increase tab height */
            min-width: 160px !important;  /* Set minimum width for tabs */
            white-space: pre-wrap;
            background-color: #F0F2F6;
            border-radius: 8px 8px 0px 0px;
            padding: 15px 20px !important;  /* Increase padding inside tabs */
            font-weight: 500;
        }

        /* Make tab text bold */
        .stTabs [data-baseweb="tab"] [data-testid="stMarkdownContainer"] p {
            font-weight: bold !important;
            font-size: 18px !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF;
            border-top: 3px solid #4B89DC;
        }

        /* Button styling */
        button {
            background-color: #4B89DC !important;
            color: white !important;
            border-radius: 5px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
        }

        /* Input field styling */
        .stTextInput > div > div > input {
            border-radius: 5px;
        }

        /* Table styling */
        .stTable {
            border-radius: 5px;
            overflow: hidden;
        }

        .stTable thead tr th {
            background-color: #4B89DC;
            color: white;
        }

        /* Results container */
        .results-container {
            border: 1px solid rgba(75, 137, 220, 0.2);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-top: 1rem;
            background-color: #F8F9FA;
        }
        </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)


def display_app_header(title="Groq Whisper WLTS Demo", subtitle="Advanced audio processing with Groq's whisper-large-v3-turbo model"):
    """Display the application header with title and subtitle."""
    header_html = f'<div class="main-header"><h1 style="margin: 0; font-size: 2.2rem;">🎵 {title}</h1><p style="margin: 0.5rem 0 0 0;">{subtitle}</p></div>'
    st.markdown(header_html, unsafe_allow_html=True)


def create_styled_container(key, content_function, title=None, description=None):
    """Create a styled container with optional title and description."""
    with stylable_container(
        key=key,
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: 1.5rem;
                background-color: #FFFFFF;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
            }

            h3 {
                color: #4B89DC;
                margin-top: 0;
                margin-bottom: 1rem;
                font-size: 1.5rem;
            }
            """,
    ):
        if title:
            st.markdown(f"### {title}")
        if description:
            st.write(description)

        # Execute the content function inside the container
        content_function()


def display_footer():
    """Display a styled footer at the bottom of the app."""
    st.markdown("---")
    with stylable_container(
        key="footer",
        css_styles="""
            {
                text-align: center;
                color: #6c757d;
                padding: 1rem;
            }
            """,
    ):
        st.markdown("Powered by Groq's whisper-large-v3-turbo model | Created with Streamlit")


def display_word_search_results(found_instances, audio_file=None, transcription=None):
    """Display search results in a styled table and optionally show audio player"""
    if found_instances:
        with stylable_container(
            key="results_container",
            css_styles="""
                {
                    border: 1px solid rgba(75, 137, 220, 0.2);
                    border-radius: 0.5rem;
                    padding: 1rem;
                    margin-top: 1rem;
                    background-color: #F8F9FA;
                }
                """,
        ):
            st.success(f"Found {len(found_instances)} instances")

            if audio_file:
                st.subheader("Audio")
                audio_html = get_audio_player_html(audio_file)
                st.markdown(audio_html, unsafe_allow_html=True)

            # Display results in a table
            st.subheader("Results")

            # Create a table for the results
            results_table = []
            for i, instance in enumerate(found_instances):
                results_table.append(
                    {
                        "Instance": i + 1,
                        "Word": instance["word"],
                        "Start Time": f"{int(instance['start'] // 60)}:{int(instance['start'] % 60):02d}",
                        "End Time": f"{int(instance['end'] // 60)}:{int(instance['end'] % 60):02d}",
                    }
                )

            st.table(results_table)
    else:
        st.warning("No instances found")


def display_badge():
    """Display the PBG badge in the corner of the app."""
    # Path to the SVG file
    svg_path = os.path.join("static", "images", "PBG mark2 color.svg")

    # Read the SVG file and encode it as base64
    with open(svg_path, "rb") as f:
        svg_data = f.read()

    b64_svg = base64.b64encode(svg_data).decode("utf-8")

    badge_html = f"""
    <style>
    .badge-container {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        width: 100px;
        height: auto;
    }}
    </style>
    <div class="badge-container">
        <img src="data:image/svg+xml;base64,{b64_svg}" alt="PBG Badge" width="100%">
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)
