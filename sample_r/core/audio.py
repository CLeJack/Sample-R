import pandas as pd
import numpy as np
import wave

from sample_r.core import files as IO
from pathlib import Path

class AudioData:
    FRAME_SIZE = 2048
    NYQUIST = FRAME_SIZE//2

    def __init__(self, path: Path, id: int = 0, analysis_type = 0):
        self.path = Path(path)
        self.id = id
        self.name = self.path.stem

        self.srate = 0
        self.data = np.array([], dtype=np.float32)
        self.start_ref = 0 #center of "mass" used to automatically get the highest volume area of the audio
        self.start_index = 0
        self.end_index = 0
        self.roll = 0
        
        # Analysis Placeholders
        self.spectrum = np.zeros(1)

        self.harmonics = np.zeros(1)
        self.hview = np.zeros(1)
        self.analysis = pd.DataFrame()
        self.analysis_type = analysis_type
        self.quantization_level = 10
        self.frame = np.zeros(AudioData.FRAME_SIZE)

        self._load_audio()

    def _load_audio(self):
        try:
            with wave.open(str(self.path), 'rb') as wf:
                nchannels = wf.getnchannels()
                self.srate = wf.getframerate()
                nframes = wf.getnframes()


                raw_data = np.frombuffer(wf.readframes(nframes), dtype=np.int16)

                # Handle Interleaving (Stereo to Mono)
                if nchannels > 1:
                    # Reshape to [nframes, nchannels]
                    reshaped = raw_data.reshape(-1, nchannels)
                    # Mean across channels for a proper mono mixdown
                    self.data = reshaped.mean(axis=1)
                else:
                    self.data = raw_data.astype(np.float32)

                #Normalize
                self.data /= np.max(np.abs(self.data)) + 1

                self.end_index = len(self.data) - 1
                

                self.max_var_start()

                if len(self.data) < AudioData.NYQUIST:
                    self.data = np.pad(self.data, (0,AudioData.NYQUIST - len(self.data)), mode='constant', constant_values=0)
    
                
                self.spectrum = np.zeros(AudioData.NYQUIST)
                self.harmonics = np.zeros(AudioData.NYQUIST)
                

        except Exception as e:
            print(f"~~~~ Error importing {self.id}) {self.name} ~~~~\n{e}")

    def com_start(self):
        #center of mass or energy
        numerator = np.sum(np.abs(self.data) * np.arange(self.data.size))
        denominator = np.sum(np.abs(self.data))
        
        self.start_ref = np.round(numerator/denominator).astype(int) #nearest index
        self.start_ref = self.end_index//2 if self.start_ref > self.end_index else self.start_ref # the true path shouldn't be possible, but just in case

        s = int(self.start_ref - AudioData.FRAME_SIZE//4) 
        e = int(self.start_ref + AudioData.FRAME_SIZE//4)
        
        # orient the initial analysis to include the frame size centered around the point of highest energy
        # this will typically be associated with the initial transient or the peak of a swell
        # self.start_index = s if s > self.start_index else self.start_index
        # self.end_index = e if e < self.end_index else self.end_index
        self.set_start_index(s)
    
    def max_var_start(self):
        #df['rolling_var'] = df['values'].rolling(window=3).var()
        df = pd.DataFrame({0:np.diff(self.data)})
        ref = df[0].rolling(window=max(len(self.data)//100, 2)).var().values
        ref = np.nan_to_num(ref, nan=0)
        self.start_ref = np.argmax(ref)

        self.set_start_index(self.start_ref)

    def sample_limit(self):
        return max(0, len(self.data) - AudioData.NYQUIST)

    def set_start_index(self, ind):
        ind = int(ind)
        ind = 0 if ind < 0 else ind
        lim = self.sample_limit()
        ind = lim if ind > lim else ind
        self.start_index = ind
        self.set_end_index(self.start_index + AudioData.NYQUIST)

    def set_end_index(self, ind):
        ind = 2 if ind < 2 else ind
        ind = len(self.data) if ind > len(self.data) else ind
        self.end_index = ind
    
    def set_offset_index(self, val):
        ind = val + self.start_index
        ind = len(self.data) - 1 if ind > len(self.data) - 1 else ind
        ind = AudioData.NYQUIST if ind > AudioData.NYQUIST else ind
        self.end_index = ind
        self.audio_offset = self.end_index - self.start_index
    
    def set_spectrum(self):
        e = self.start_index + AudioData.NYQUIST
        e = len(self.data) if len(self.data) < AudioData.NYQUIST else e

        signal = self.data[self.start_index: self.end_index]
        if len(signal) < AudioData.NYQUIST:
            p = AudioData.NYQUIST - len(signal)
            signal = np.pad(signal, (0,p), mode='constant',constant_values=0)

        signal = signal * np.hanning(signal.size)
        result = np.real(np.abs(np.fft.fft(signal)))
        result[signal.size//2:] = 0
        self.spectrum = result
        
        return self.spectrum


    def analyze(self):
        # binary spectrum resolution reduction
        try:        
            iterations = int(np.log2(len(self.spectrum)))
            
            df = pd.DataFrame(self.spectrum,columns = ['spec'])
            data = {0: df['spec'].values}
            for i in range(1, iterations):
                df['ind'] = np.arange(len(df))//pow(2,i)
                harmonics = df.groupby('ind').transform('max').values.flatten()
                data[i] = harmonics

            self.analysis = pd.DataFrame(data)
        except Exception as e:
            print(f'Error analyzing file: {self.id}) {self.name}')

    def set_quantization_level(self):
        try:
            data = self.analysis.iloc[0,:]
            ref = np.mean(data)
            data = data[data <= ref]
            self.quantization_level = int(data[-1:].index[0])
        except Exception as e:
            print(f'Error setting compression of {self.name}, using default')
            self.quantization_level = 0

    def create_harmonics(self):

            # ind = self.quantization_level
            # ind = min(ind, len(self.analysis.columns)-1)
            harmonics = []
            for i in range(len(self.analysis.columns)):
                data = self.analysis[i]

                d = data.diff().fillna(data[0])
                d = data[d != 0].values
                harmonics.append(d)


            self.harmonics = harmonics
            self.roll_harmonics(self.roll)
            

    def set_harmonic(self, index, val):
        self.harmonics[index] = val
        self.roll_harmonics(self.roll)

    def roll_harmonics(self, n):
        self.hview = np.roll(self.harmonics[self.quantization_level],n)
        if n > 0:
            self.hview[:n] = 0
        if n < 0:
            self.hview[len(self.hview) + n:] = 0
                
    def resynthesize(self, harmonics):
        output = []
        for i,amp in enumerate(harmonics[:AudioData.NYQUIST]):
            xs = np.linspace(0,2*np.pi,AudioData.FRAME_SIZE, endpoint=False) * i
            # amp = np.pad(amp, (0,AudioData.FRAME_SIZE - l), mode = 'constant', constant_values=0)
            output.append(amp * np.sin(xs))
        
        output = np.array(output)
        output = output.sum(axis=0)
        _m = np.abs(output).max()
        output = output/_m if _m > 0 else output
        return output

    def resynthesize_cycle(self):
        self.frame = self.resynthesize(self.hview)
    
    def resynthesize_quant(self):
        frames = []
        for h in self.harmonics[:len(self.harmonics) - 1]: # no need to include last frame which is always 0
            print(len(h))
            f = self.resynthesize(h)
            frames.append(f)

        n = len(frames) * AudioData.FRAME_SIZE
        frames = np.array(frames)
        frames = frames.reshape((1,n))
        return frames


    def full_process(self, internal_quantize = True):
        self.set_spectrum()
        self.analyze()
        if internal_quantize:
            self.set_quantization_level()
        self.create_harmonics()
        self.resynthesize_cycle()
