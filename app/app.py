import os
import streamlit as st
import tempfile
import time
import subprocess
from karaoke_maker import extract_audio, separate_vocals, transcribe_audio, create_subtitles, create_final_video

# Page configuration
st.set_page_config(
    page_title="Karaoke Generator",
    page_icon="🎵",
    layout="wide"
)

# App title and description
st.title("🎵 Karaoke Generator")
st.markdown("""
Upload a music video or audio file and this app will:
1. Remove vocals from the audio
2. Generate lyrics as subtitles
3. Create a karaoke version with instrumental track and synchronized lyrics
""")

# Show warning about resource constraints
st.warning("""
**Resource Requirements:**
- For best results, use videos under 2 minutes in length
- The 2stems model requires less memory and is recommended
- Processing can take 5-15 minutes depending on video length
""")

# Create upload section with file size limit info
uploaded_file = st.file_uploader("Upload your music video (max 100MB recommended)",
                                 type=['mp4', 'mkv', 'avi', 'mov', 'webm'])

# Settings section with expander
with st.expander("Settings"):
    whisper_model = st.selectbox(
        "Transcription Model",
        ["tiny", "base"],  # Only offer lightweight models
        index=0,  # Default to tiny
        help="Tiny is fastest but less accurate, Base is a good balance"
    )

    separation_model = st.selectbox(
        "Vocal Separation Model",
        ["spleeter:2stems", "spleeter:4stems"],
        index=0,  # Default to 2stems
        help="2stems requires less memory, 4stems may give better results but needs more memory"
    )

    subtitle_font_size = st.slider(
        "Subtitle Font Size",
        min_value=12,
        max_value=48,
        value=24,
        help="Size of subtitle text in output video"
    )

    keep_temp_files = st.checkbox(
        "Keep temporary files",
        value=False,
        help="Save intermediate files (audio, subtitles) for debugging"
    )


# Function to check video length
def get_video_duration(video_path):
    try:
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return float(output)
    except:
        return None


# Process button
if uploaded_file is not None:
    col1, col2 = st.columns(2)

    with col1:
        st.video(uploaded_file)
        file_details = {"Filename": uploaded_file.name, "File size": f"{uploaded_file.size / 1024 / 1024:.2f} MB"}
        st.write(file_details)

    with col2:
        if st.button("Generate Karaoke Version", type="primary"):
            # Check file size (100MB recommended limit)
            if uploaded_file.size > 100 * 1024 * 1024:
                st.warning(
                    f"File size is {uploaded_file.size / 1024 / 1024:.1f}MB. Large files may cause memory issues.")

            # Create working directories
            temp_dir = tempfile.mkdtemp()
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)

            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Save uploaded file
                status_text.text("Saving uploaded file...")
                input_path = os.path.join(temp_dir, "input_video.mp4")
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                progress_bar.progress(10)

                # Check video duration
                duration = get_video_duration(input_path)
                if duration and duration > 300:  # 5 minutes
                    st.warning(
                        f"Video is {duration / 60:.1f} minutes long. Processing may fail due to memory constraints.")

                # Extract audio
                status_text.text("Extracting audio from video...")
                audio_path = os.path.join(temp_dir, "original_audio.wav")
                extract_audio(input_path, audio_path)
                progress_bar.progress(20)

                # Separate vocals with memory optimization settings
                status_text.text(f"Separating vocals using {separation_model} (this may take several minutes)...")
                try:
                    instrumental_path = separate_vocals(audio_path, temp_dir, model=separation_model)
                    progress_bar.progress(50)
                except subprocess.CalledProcessError as e:
                    if "4stems" in separation_model:
                        st.warning("The 4stems model failed due to memory limits. Falling back to 2stems...")
                        instrumental_path = separate_vocals(audio_path, temp_dir, model="spleeter:2stems")
                        progress_bar.progress(50)
                    else:
                        raise e

                # Transcribe audio - use tiny model for longer audio
                if duration and duration > 180 and whisper_model != "tiny":
                    st.info(f"Video is {duration / 60:.1f} minutes long. Using 'tiny' model for faster processing.")
                    actual_model = "tiny"
                else:
                    actual_model = whisper_model

                status_text.text(f"Transcribing vocals using {actual_model} model...")
                segments = transcribe_audio(audio_path, model_name=actual_model)
                progress_bar.progress(70)

                # Create subtitles
                status_text.text("Creating subtitle file...")
                subtitle_path = os.path.join(temp_dir, "lyrics.srt")
                create_subtitles(segments, subtitle_path)
                progress_bar.progress(80)

                # Create final video with reduced quality for speed and memory savings
                status_text.text("Creating final karaoke video...")
                output_path = os.path.join(output_dir, "karaoke_output.mp4")
                create_final_video(
                    input_path,
                    instrumental_path,
                    subtitle_path,
                    output_path,
                    subtitle_font_size=subtitle_font_size
                )
                progress_bar.progress(100)

                # Display results
                status_text.text("✅ Karaoke video generated successfully!")

                # Show download button
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Karaoke Video",
                        data=file,
                        file_name="karaoke_video.mp4",
                        mime="video/mp4"
                    )

                # Preview output
                st.video(output_path)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Try these solutions:")
                st.markdown("""
                1. Use a shorter video (less than 2 minutes)
                2. Select the 2stems model instead of 4stems
                3. Use the 'tiny' transcription model
                4. Reduce the video resolution before uploading
                """)

# Footer
st.markdown("---")
st.markdown("Created with ❤️ by VietDucFCB | [GitHub](https://github.com/VietDucFCB)")