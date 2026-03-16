import pandas as pd
import numpy as np
import wave

import tuning as T
import matrices as M
from reexport import export_wavetable

class AudioData:

    def __init__(self, path, id, framesize, min_freq):


        self.min_freq = min_freq
        self.path = path
        self.id = id
        self.framesize = framesize

        self.srate = 0
        self.min_freq = 0
        self.data= np.zeros(1)
        self.name = ""
        self.nspectrum = [] # note (12tet) based frequency spectrum
        self.hspectrum = [] # harmonic based frequency spectrum built from the fundamental
        self.nmat = [] # note based dft matrix
        self.hmat = [] # harmonic based dft matrix
        self.nfreqs = [] # note frequencies
        self.hfreqs = [] # harmonic frequencies
        self.frame = [] # the frame meant for export
        self.df = None
        self.fundamental_ind = 0 # dervied from nfreqs
        self.fundamental_freq = 0

        try:
            with wave.open(str(path), 'rb') as wf:

                nchannels = wf.getnchannels() 
                self.srate = wf.getframerate() 

                self.data = np.frombuffer(wf.readframes(wf.getnframes()), np.int16)

                # no stereo allowed
                if nchannels> 1:
                    self.data = self.data.sum(axis = 0)

                # assuming some path and .wav files only for input
                self.path = path
                self.name = path.stem
                

        except Exception as e:
            print("~~~~ Error during import ~~~~")
            print(e)
            print("~~~~ Error during import ~~~~")

class Audio2WavetableN(AudioData):

    def __init__(self, path, id, framesize = 2048, min_freq = 0):
        super().__init__(path, id, framesize, min_freq)

    
    def set_fundamental(self):
        
        df = pd.DataFrame(self.nspectrum, columns = ['spec'])
        df = df.reset_index()
        s = df['spec']
        df = df[(s.shift(1) <= s) & (s > s.shift(-1))].copy() #peaks
        s = df['spec']
        df['threshold'] = np.median(s) + np.mean(np.abs(s - np.median(s))) * 3
        df = df[df['spec'] > df['threshold']]
        self.fundamental_ind = df['index'].min()
        self.fundamental_freq = self.nfreqs[self.fundamental_ind]
        self.df = df
    
    def resynthesize_data(self):
        output = []
        for i,amp in enumerate(self.hspectrum):
            xs = np.linspace(0,2*np.pi,self.framesize, endpoint=False) * i
            output.append(amp * np.sin(xs))
        
        output = np.array(output)
        output = output.sum(axis=0)
        output = output/np.abs(output).max()
        self.frame = output

    def analyze_12tet(self):
        self.nfreqs=T.get_freqs()

        #restrict to nyquist for the current file
        self.nfreqs = self.nfreqs[self.nfreqs < self.srate//2]
        self.nfreqs = self.nfreqs[self.nfreqs > self.min_freq]

        if self.srate > self.data.size:
            # z = np.zeros(self.data.size)
            # z[self.data.size//2:] = 1 
            # self.data = self.data * np.hanning(self.data.size)

            p = self.srate - self.data.size
            self.data = np.pad(self.data,(0,p),mode="constant",constant_values=0)
        elif self.srate < self.data.size:
            # rows = self.data.size//self.srate
            # self.data = self.data[:self.srate * rows ]
            
            # self.data = self.data.reshape(rows, self.srate)

            # clipping this to the first second of data for now
            self.data = self.data[:self.srate].copy()

        

        self.nmat = M.cmatrix(self.srate, self.srate,self.nfreqs)
        self.nspectrum = M.dct(self.nmat, self.data)
        
        self.set_fundamental()
        
    
    def process_tonal(self, do_12tet = True, freq_from_file = False):
        try:
            if freq_from_file:
                self.fundamental_freq = T.pitch_class_to_freq(str(self.path))
            elif do_12tet:
                self.analyze_12tet()
            
            self.hfreqs = self.fundamental_freq * (np.arange(64)+1)
            self.hfreqs = self.hfreqs[ self.hfreqs <= self.srate//2]
            
            self.hmat = M.cmatrix(self.data.size, self.srate, freqs = self.hfreqs)
            self.hspectrum = M.dct(self.hmat,self.data)

            self.resynthesize_data()

        except Exception as e:
            print(f'\n~~~Error at file {self.name}, id {self.id}~~~')
            print(e)
            print('~~~~~~\n')
    
    def reprocess_ind(self, index):
        #reprocess the signal with a manually set fundamental index
        l = len(self.nfreqs)
        if l > 0 and index < l and index > 0:
            self.fundamental_ind = index
            self.fundamental_freq = self.nfreqs[index]
            self.process_tonal(do_12tet=False)
        else:
            print("\nReprocessing by index can only be done if a tonal analysis has already been completed\n")

    def reprocess_freq(self, freq):
        freq = 1 if freq < 1 else freq

        nyquist =self.srate//2
        freq = nyquist if freq > nyquist else freq
        
        self.process_tonal(do_12tet=False)

        print(f"Frequency outside of 1hz and {nyquist}hz will be clamped")
    
    

        

    def export(self, path = "./", prepend = ""):
        if(len(self.frame) == self.framesize):
            export_wavetable(self.frame, path = path, filename = self.name, prepend = prepend)
        else:
            print(f"\nCould not export incompleted or partial wavetable of file {self.name}\n")
    
    def __str__(self):
        return f'\nfile name: {self.name}\
                \nsample rate: {self.srate}\
                \nfundamental frequency index: {self.fundamental_ind}\
                \nfundamental frequency: {self.fundamental_freq}\
                \nharmonics : {len(self.hfreqs)}\n'