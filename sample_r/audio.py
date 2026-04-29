import pandas as pd
import numpy as np
import wave

import tuning as T
import matrices as M
import files as IO
from pathlib import Path

class AudioData:
    def __init__(self, path: Path, id: int = 0, framesize: int = 2048):
        self.path = Path(path)
        self.id = id
        self.framesize = framesize
        self.name = self.path.stem

        self.srate = 0
        self.data = np.array([], dtype=np.float32)
        self.com = 0 #center of "mass" used to automatically get the highest volume area of the audio
        self.start_index = 0
        self.end_index = 0
        
        # Analysis Placeholders
        self.spectrum = np.zeros(1)
        self.fundamental_ind = 0

        self.harmonics = np.zeros(1)
        self.frame = np.zeros(framesize)

        self._load_audio()

    def _load_audio(self):
        try:
            with wave.open(str(self.path), 'rb') as wf:
                nchannels = wf.getnchannels()
                self.srate = wf.getframerate()
                nframes = wf.getnframes()

                # Read raw bytes and convert to int16
                raw_data = np.frombuffer(wf.readframes(nframes), dtype=np.int16)

                # Handle Interleaving (Stereo to Mono)
                if nchannels > 1:
                    # Reshape to [nframes, nchannels]
                    reshaped = raw_data.reshape(-1, nchannels)
                    # Mean across channels for a proper mono mixdown
                    self.data = reshaped.mean(axis=1)
                else:
                    self.data = raw_data.astype(np.float32)

                # Normalize to -1.0 to 1.0 range
                self.data /= 32768.0
                self.end_index = len(self.data) - 1
                
                numerator = np.sum(np.abs(self.data) * np.arange(self.data.size))
                denominator = np.sum(np.abs(self.data))
                
                self.com = np.round(numerator/denominator).astype(int) #nearest index
                self.com = self.end_index if self.com > self.end_index else self.com 

                if(self.srate < self.end_index):
                    # set analysis window around center of energy for the signal
                    offset = self.srate//2
                    start = self.com - offset
                    end = self.com + offset

                    if(end <= self.end_index and start >= self.start_index):
                        self.start_index = start
                        self.end_index = end
                
                self.spectrum = np.zeros(self.end_index - self.start_index)
                self.harmonics = np.zeros(64)
                

        except Exception as e:
            print(f"~~~~ Error importing {self.name} ~~~~\n{e}")

    def set_start_index(self, ind):
        self.start_index = ind

    def set_end_inex(self, ind):
        self.end_index = ind
    
    def set_spectrum(self):
        signal = self.data[self.start_index: self.end_index]
        signal = signal * np.hanning(signal.size)
        result = np.real(np.abs(np.fft.fft(signal)))
        result[signal.size//2:] = 0
        self.spectrum = result
        
        return self.spectrum

    def set_harmonics(self, limit = 128):
        # this algo takes a given frequency spectrum of an arbitrary size, 
        # and reduces it to a number of harmonics set by the limit
        # being greedy (i.e. going over 128) will produce a ringing like output during single cycle resynthesis

        iterations = int(np.log2(self.spectrum.size)) - int(np.log2(limit))
        
        df = pd.DataFrame(self.spectrum,columns = ['spec'])

        for i in range(iterations):
            df['ind'] = np.arange(len(df))//2
            harmonics = df.groupby('ind').max()['spec'].values
            harmonics[0] = 0
            df = pd.DataFrame(harmonics, columns = ['spec'])
        harmonics = harmonics[:limit]
        harmonics = harmonics/np.sum(harmonics)
        self.harmonics = harmonics


    def resynthesize_cycle(self, limit = 128):
        output = []
        end = min(limit, self.harmonics.size)
        for i,amp in enumerate(self.harmonics[:end]):
            xs = np.linspace(0,2*np.pi,self.framesize, endpoint=False) * i
            output.append(amp * np.sin(xs))
        
        output = np.array(output)
        output = output.sum(axis=0)
        output = output/np.abs(output).max()
        self.frame = output
            

        

    def export(self, path = "./", prepend = ""):
        if(len(self.frame) == self.framesize):
            IO.export_wavetable(self.frame, path = path, filename = self.name, prepend = prepend)
        else:
            print(f"\nCould not export incompleted or partial wavetable of file {self.name}\n")
    
    def __str__(self):
        return f'\nfile name: {self.name}\
                \nsample rate: {self.srate}\
                \nfundamental frequency index: {self.fundamental_ind}\
                \nharmonics : {len(self.harmonics)}\n'