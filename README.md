# Video Frame Capturer

A desktop app for loading videos and saving individual frames as images.

## Setup

Requires Python 3.8+

```bash
pip install -r requirements.txt
```

**Note:** `tkinter` comes pre-installed with Python on most systems. If you get a `ModuleNotFoundError` for tkinter:
- **macOS:** `brew install python-tk`
- **Ubuntu/Debian:** `sudo apt install python3-tk`

## Usage

```bash
python frame_capture.py
```

1. Click **Load Video** to open a video file (mp4, avi, mov, mkv, flv, wmv)
2. Use **Play/Pause** to play the video or step through with **Prev Frame / Next Frame**
3. Adjust playback speed with the **Speed** dropdown
4. Click **Capture** to save the current frame
5. Use the **slider** at the bottom to scrub to any point in the video

Captured frames are saved to a `frames/` folder in the project directory as JPGs, named `{video_name}_{number}.jpg`.
