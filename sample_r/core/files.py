import os
from pathlib import Path
import wave
import numpy as np



def get_files_in_cwd():
    return get_files(Path.cwd())

def get_files(path):
    if type(path) is type([]):
        #file dialog returned explicit file list
        files = path
    else:
        # folder returned
        p = Path(path)
        if not p.is_dir():
            return []

        # iterdir() is cleaner than os.listdir + mapping
        files = [f for f in p.iterdir() if f.is_file()]

    files = list(filter(lambda x: '.wav' in str(x),files))

    return files


def export_frame(data, path = "./", filename = "output", prepend = "", srate = 44100, channels = 1, sample_width = 2):
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

    # print(f"Successfully wrote {filename}")

def consolidated_export(data, path = "./", filename = "output",srate = 44100, channels = 1, sample_width = 2):
     wt = [d.frame for d in data]
     wt = np.array(wt)
     export_frame(wt,path, filename + ".wav", '', srate, channels, sample_width)

def export_wavetable(data, path = "./", filename = "output", prepend = "", srate = 44100, channels = 1, sample_width = 2):
    assert isinstance(data, list)
    d = np.array(data)
    frame_size = d.size[0] * d.size[1]
    d = d.reshape((1,frame_size))
    export_frame(d, path, filename, prepend, srate, channels, sample_width)