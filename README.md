# Algorithmic Karaoke Generator

## Overview

The Algorithmic Karaoke Generator is a digital signal processing (DSP) based application that converts music videos into karaoke versions by:

1. Removing vocals from the audio using spectral analysis techniques
2. Creating synchronized subtitles using energy detection
3. Combining the instrumental track and subtitles into a karaoke video

Unlike traditional karaoke generators that rely on heavy machine learning frameworks, this application uses fundamental signal processing algorithms, making it lightweight and memory-efficient.

## Features

- **Multiple Vocal Removal Techniques**:
  - Spectral Subtraction
  - Center Channel Cancellation
  - Adaptive Filtering
  - Combined methods for better quality

- **Automatic Subtitle Generation**:
  - Energy-based vocal detection
  - Evenly spaced placeholder subtitles
  - Customizable subtitle appearance

- **Supports Various Formats**:
  - Video: MP4, MKV, AVI, MOV, WEBM
  - Audio: MP3, WAV

- **User-Friendly Interface**:
  - Intuitive Streamlit web UI
  - Real-time processing feedback
  - Preview and download options

## Tools & Technologies

### Core Technologies
- **Python 3.10+**: Primary programming language
- **NumPy & SciPy**: Scientific computing libraries for signal processing
- **FFmpeg**: Audio/video processing and manipulation
- **Streamlit**: Web interface framework

### Signal Processing Techniques
- Fourier Transforms (FFT/IFFT)
- Bandpass Filtering
- Energy-based Voice Activity Detection
- Spectral Subtraction
- Phase Cancellation

### Dependencies
- numpy (≥1.20.0): Array operations and numerical computing
- scipy (≥1.8.0): Signal processing functions
- streamlit (≥1.22.0): Web interface
- ffmpeg: External dependency for media processing

## Installation

### Prerequisites
- Python 3.10 or higher
- FFmpeg installed and available in your PATH
- Docker (optional, for containerized deployment)

### Method 1: Docker Installation (Recommended)

1. **Clone the repository or download the project files**:
   ```bash
   git clone https://github.com/VietDucFCB/algorithmic-karaoke.git
   cd algorithmic-karaoke
   ```

2. **Build and run the Docker container**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Access the application**:
   Open your browser and navigate to http://localhost:8501

### Method 2: Local Installation

1. **Install FFmpeg**:
   
   **For Windows**:
   - Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Add to your PATH environment variable
   
   **For macOS**:
   ```bash
   brew install ffmpeg
   ```
   
   **For Linux**:
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

2. **Set up Python environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements_minimal.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Start the application** as described in the installation section
2. **Upload your music video or audio file** using the file uploader
3. **Configure settings**:
   - Choose a vocal separation method based on your needs
   - Select subtitle generation method
   - Adjust subtitle font size
4. **Click "Generate Karaoke Version"** and wait for processing to complete
5. **Preview and download** your karaoke video

## Technical Details

### Vocal Separation Algorithms

#### Center Channel Cancellation
This technique exploits the fact that vocals are usually panned center in the stereo mix. By subtracting the right channel from the left (and vice versa), we can reduce the centered content (primarily vocals).

```python
# Simplified example
left = audio_data[:, 0]
right = audio_data[:, 1]
center_removed_left = left - right
center_removed_right = right - left
instrumental = np.column_stack((center_removed_left, center_removed_right))
```

#### Spectral Subtraction
This method operates in the frequency domain, identifying and attenuating frequencies characteristic of human voice (primarily 300Hz-3kHz).

```python
# Simplified explanation
# 1. Convert audio to frequency domain using FFT
# 2. Create a mask that attenuates frequencies in vocal range
# 3. Apply mask to frequency data
# 4. Convert back to time domain using IFFT
```

#### Combined Method
Uses multiple techniques in sequence for improved vocal removal quality.

### Vocal Detection Algorithm

The application uses energy-based detection to find segments with vocal activity:

1. Calculate the energy of short frames (25ms)
2. Normalize the energy values
3. Apply a threshold to detect high-energy segments (likely vocals)
4. Group adjacent frames into continuous segments
5. Filter out segments that are too short

### Video Demo

https://drive.google.com/file/d/1jqXl7kL_qRXacimsL8gqPGAkMotJMbBA/view?usp=sharing

## Performance Optimization

- **Chunked Processing**: Long audio files are processed in small chunks (20-30 seconds) to minimize memory usage
- **Downsampling**: Audio is often downsampled to 16kHz mono for processing
- **Efficient File Handling**: Temporary files are cleaned up immediately when no longer needed

## Troubleshooting

### Common Issues and Solutions

**Issue**: FFmpeg not found
- **Solution**: Ensure FFmpeg is installed and in your PATH environment variable

**Issue**: Poor vocal removal quality
- **Solution**: Try different separation methods; stereo tracks with centered vocals work best

**Issue**: Memory errors with large files
- **Solution**: The application should handle this by chunking, but try with shorter files if problems persist

**Issue**: Docker container fails to start
- **Solution**: Check Docker logs with `docker-compose logs -f`

## Limitations

- The algorithmic approach doesn't match the quality of machine learning methods for vocal isolation
- Works best with stereo audio where vocals are panned center
- Subtitles are placeholders only, not actual transcribed lyrics

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FFmpeg developers for the essential audio/video processing tools
- Streamlit team for the intuitive web interface framework
- NumPy and SciPy contributors for scientific computing tools

---

Created by VietDucFCB | Last updated: 2025-04-13
```
