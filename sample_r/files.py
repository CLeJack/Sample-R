import os
from pathlib import Path
import wave
import numpy as np



def get_files_in_cwd():
    return get_files(Path.cwd())

def get_files(path):
    p = Path(path)
    if not p.is_dir():
        return []

    # iterdir() is cleaner than os.listdir + mapping
    files = [f for f in p.iterdir() if f.is_file()]

    files = list(filter(lambda x: '.wav' in str(x),files))

    return files


def export_wavetable(data, path = "./", filename = "output", prepend = "", srate = 44100, channels = 1, sample_width = 2):
    p = Path(path)
    filename = prepend+filename+".wav"
    p = p / filename

    d = data * (0.5 * 2**16 - 1)
    audio_frames = d.astype(np.int16).tobytes()

    # Write the WAV file
    with wave.open(str(p), 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(srate)
        wf.writeframes(audio_frames)

    print(f"Successfully wrote {filename}")

def consolidated_export(data, path = "./", filename = "output",srate = 44100, channels = 1, sample_width = 2):
     wt = [d.frame for d in data]
     wt = np.array(wt)
     export_wavetable(wt,path, filename, '', srate, channels, sample_width)