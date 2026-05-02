import pandas as pd
import numpy as np
import wave

from sample_r.core import files as IO
from pathlib import Path

class AudioData:
    def __init__(self, path: Path, id: int = 0, analysis_type = 0):
        self.path = Path(path)
        self.id = id
        self.framesize = 2048
        self.name = self.path.stem

        self.srate = 0
        self.data = np.array([], dtype=np.float32)
        self.com = 0 #center of "mass" used to automatically get the highest volume area of the audio
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
        self.frame = np.zeros(self.framesize)

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
                
                #center of mass or energy
                numerator = np.sum(np.abs(self.data) * np.arange(self.data.size))
                denominator = np.sum(np.abs(self.data))
                
                self.com = np.round(numerator/denominator).astype(int) #nearest index
                self.com = self.end_index//2 if self.com > self.end_index else self.com # the true path shouldn't be possible, but just in case
                
                # using 1024 as the initial range instead of 2048
                # associated with slight under 50 hz pr A1 at 48khz sample rate
                # this is a decent lower bound for tonal information
                s = int(self.com - self.framesize//4) 
                e = int(self.com + self.framesize//4)
                
                # orient the initial analysis to include the frame size centered around the point of highest energy
                # this will typically be associated with the initial transient or the peak of a swell
                self.start_index = s if s > self.start_index else self.start_index
                self.end_index = e if e < self.end_index else self.end_index

    
                
                self.spectrum = np.zeros(self.end_index - self.start_index)
                self.harmonics = np.zeros(64)
                

        except Exception as e:
            print(f"~~~~ Error importing {self.id}) {self.name} ~~~~\n{e}")

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


    def analyze(self):
        # binary spectrum resolution reduction
        try:

            f = 0
            match self.analysis_type:
                case 0:
                    f = 'max'
                case 1:
                    f = 'sum'
                case _:
                    f = 'max'
    
                    

            iterations = int(np.log2(len(self.spectrum)))
            
            df = pd.DataFrame(self.spectrum,columns = ['spec'])
            data = {0: df['spec'].values}
            for i in range(1, iterations):
                df['ind'] = np.arange(len(df))//pow(2,i)
                harmonics = df.groupby('ind').transform(f).values.flatten()
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
            i = int(np.log2(len(self.spectrum)))
            if i < 10:
                # on error just go to the default if the spectrum size is already under 2^10
                self.quantization_level = 0
            else:
                # compression level of 10 is associated with a framesize of 2^10 or 1024
                # i.e. if the sample size of the spectrum is greater than 1024
                # set index associated with a size of 1024 bins; the ifft will map this back to 2048 
                self.quantization_level = i - 10

    def create_harmonics(self):

            ind = self.quantization_level
            ind = min(ind, len(self.analysis.columns)-1)
            data = self.analysis[ind]

            t = data.diff().fillna(data[0])
            t = data[t != 0].values

            self.harmonics = t
            self.roll_harmonics(self.roll)
            

    def set_harmonic(self, index, val):
        self.harmonics[index] = val
        self.roll_harmonics(self.roll)

    def roll_harmonics(self, n):
        self.hview = np.roll(self.harmonics,n)
        if n > 0:
            self.hview[:n] = 0
        if n < 0:
            self.hview[len(self.hview) + n:] = 0
                

    def resynthesize_cycle(self):
        limit = self.framesize//2
        output = []
        end = min(limit, len(self.hview))


        for i,amp in enumerate(self.hview[:end]):
            xs = np.linspace(0,2*np.pi,self.framesize, endpoint=False) * i
            output.append(amp * np.sin(xs))
        
        output = np.array(output)
        output = output.sum(axis=0)
        _m = np.abs(output).max()
        output = output/_m if _m > 0 else output
        self.frame = output

    def full_process(self, internal_quantize = True):
        self.set_spectrum()
        self.analyze()
        if internal_quantize:
            self.set_quantization_level()
        self.create_harmonics()
        self.resynthesize_cycle()

            

        

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