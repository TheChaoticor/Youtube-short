
import librosa
import numpy as np

def detect_audio_energy(audio_path):
    y, sr = librosa.load(audio_path)
    energy = np.sum(librosa.feature.rms(y=y))
    return energy
