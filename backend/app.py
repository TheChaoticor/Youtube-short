
from flask import Flask, request, jsonify, send_file
from pytube import YouTube
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import whisper
import librosa
import numpy as np
import cv2

app = Flask(__name__)

# Ensure folders exist
os.makedirs("downloads", exist_ok=True)
os.makedirs("processed", exist_ok=True)

# Whisper model
model = whisper.load_model("base")  # Small free model for speech-to-text

# Download YouTube video
def download_video(youtube_url):
    yt = YouTube(youtube_url)
    video_stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
    filename = video_stream.download(output_path="downloads")
    return filename

# Extract audio and transcribe
def transcribe_audio(video_path):
    result = model.transcribe(video_path)
    return result['text']

# Audio energy detection
def detect_audio_energy(audio_path):
    y, sr = librosa.load(audio_path)
    energy = np.sum(librosa.feature.rms(y=y))
    return energy

# Scene change detection
def detect_scene_changes(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_diffs = []
    ret, prev_frame = cap.read()
    while ret:
        ret, curr_frame = cap.read()
        if not ret:
            break
        diff = cv2.absdiff(prev_frame, curr_frame)
        non_zero_count = np.count_nonzero(diff)
        frame_diffs.append(non_zero_count)
        prev_frame = curr_frame
    cap.release()
    return frame_diffs

# Create a short clip
def create_short(video_path, output_path, start_time, duration, text_overlay=None):
    clip = VideoFileClip(video_path).subclip(start_time, start_time + duration)
    if text_overlay:
        txt_clip = TextClip(text_overlay, fontsize=24, color='white').set_position('bottom').set_duration(duration)
        clip = CompositeVideoClip([clip, txt_clip])
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

@app.route("/process", methods=["POST"])
def process_video():
    data = request.json
    youtube_url = data["youtube_url"]

    try:
        # Step 1: Download the video
        video_path = download_video(youtube_url)

        # Step 2: Transcribe the audio
        transcription = transcribe_audio(video_path)

        # Step 3: Analyze audio and scene for energy and changes
        energy = detect_audio_energy(video_path)
        scene_changes = detect_scene_changes(video_path)

        # Step 4: Generate a short clip with detected content
        short_path = os.path.join("processed", "short.mp4")
        create_short(video_path, short_path, start_time=0, duration=30, text_overlay=transcription[:100])

        return send_file(short_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
