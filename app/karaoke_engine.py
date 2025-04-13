import os
import subprocess
from datetime import timedelta
import gc  # For garbage collection


def extract_audio(video_path, output_path):
    """Extract audio from video file"""
    cmd = f'ffmpeg -i "{video_path}" -q:a 0 -map a "{output_path}" -y'
    subprocess.run(cmd, shell=True, check=True)
    return output_path


def separate_vocals(audio_path, output_dir, model="spleeter:2stems"):
    """Separate vocals from music using Spleeter with memory optimizations"""
    os.makedirs(output_dir, exist_ok=True)

    # Force garbage collection before running memory-intensive process
    gc.collect()

    # For 4stems, use lower quality to save memory
    if "4stems" in model:
        # Use 16kHz sample rate and mono for processing to save memory
        # Then create a high-quality output later
        temp_audio = os.path.join(output_dir, "downsampled_audio.wav")
        downsample_cmd = f'ffmpeg -i "{audio_path}" -ar 16000 -ac 1 "{temp_audio}" -y'
        subprocess.run(downsample_cmd, shell=True, check=True)

        # Run spleeter with memory limit
        cmd = f'spleeter separate -p {model} --mwf -o "{output_dir}" "{temp_audio}"'
    else:
        # Run spleeter with default settings for 2stems
        cmd = f'spleeter separate -p {model} -o "{output_dir}" "{audio_path}"'

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        # Fallback to 2stems if 4stems fails
        if "4stems" in model:
            print("4stems model failed due to memory constraints, falling back to 2stems...")
            return separate_vocals(audio_path, output_dir, "spleeter:2stems")
        else:
            raise

    # Get path to instrumental track
    base_name = os.path.splitext(os.path.basename(audio_path))[0]

    # Different output directory structure based on model
    if "4stems" in model and os.path.exists(os.path.join(output_dir, base_name, "other.wav")):
        # For 4stems, mix drums, bass and other to create accompaniment
        drums_path = os.path.join(output_dir, base_name, "drums.wav")
        bass_path = os.path.join(output_dir, base_name, "bass.wav")
        other_path = os.path.join(output_dir, base_name, "other.wav")
        instrumental_path = os.path.join(output_dir, base_name, "accompaniment.wav")

        # Mix the stems to create accompaniment
        mix_cmd = f'ffmpeg -i "{drums_path}" -i "{bass_path}" -i "{other_path}" -filter_complex "[0:a][1:a][2:a]amix=inputs=3:dropout_transition=0" "{instrumental_path}" -y'
        subprocess.run(mix_cmd, shell=True, check=True)
        return instrumental_path
    else:
        # For 2stems, just return the accompaniment file
        return os.path.join(output_dir, base_name, "accompaniment.wav")


def transcribe_audio(audio_path, model_name="base"):
    """Transcribe vocals using Whisper with memory optimization"""
    import whisper

    # Force garbage collection
    gc.collect()

    # For longer audios, downsample first to reduce memory usage
    temp_audio = None
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{audio_path}"'
    duration_output = subprocess.check_output(duration_cmd, shell=True).decode('utf-8').strip()

    try:
        duration = float(duration_output)
        # For longer audio, use downsampling to save memory
        if duration > 180:  # For audio longer than 3 minutes
            temp_dir = os.path.dirname(audio_path)
            temp_audio = os.path.join(temp_dir, "downsampled_for_whisper.wav")
            downsample_cmd = f'ffmpeg -i "{audio_path}" -ar 16000 -ac 1 "{temp_audio}" -y'
            subprocess.run(downsample_cmd, shell=True, check=True)
            audio_path = temp_audio
    except:
        pass

    # Load model and transcribe
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)

    # Cleanup temp file if created
    if temp_audio and os.path.exists(temp_audio):
        try:
            os.remove(temp_audio)
        except:
            pass

    return result["segments"]


def create_subtitles(segments, output_path):
    """Create SRT subtitles from transcribed segments"""
    import pysrt

    subs = pysrt.SubRipFile()

    for i, segment in enumerate(segments):
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()

        # Convert time to SRT format
        start = timedelta(seconds=start_time)
        end = timedelta(seconds=end_time)

        # Create subtitle item
        item = pysrt.SubRipItem(
            index=i + 1,
            start=start,
            end=end,
            text=text
        )
        subs.append(item)

    # Save subtitles
    subs.save(output_path, encoding='utf-8')
    return output_path


def create_final_video(video_path, instrumental_path, subtitle_path, output_path, subtitle_font_size=24):
    """Create final video with instrumental audio and subtitles"""
    subtitle_path_escaped = subtitle_path.replace('\\', '\\\\').replace(':', '\\:')

    # Use a lower bitrate and preset for faster encoding
    cmd = f'ffmpeg -i "{video_path}" -i "{instrumental_path}" ' \
          f'-vf "subtitles={subtitle_path_escaped}:force_style=\'FontSize={subtitle_font_size}\'" ' \
          f'-map 0:v -map 1:a -c:v libx264 -preset faster -crf 28 -c:a aac -b:a 128k ' \
          f'"{output_path}" -y'

    subprocess.run(cmd, shell=True, check=True)
    return output_path