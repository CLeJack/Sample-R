"""
Custom Fourier Transform

A variation on the idea of the discrete fourier transform

"""
import numpy as np
import sample_r.dsp.waveforms as W


def harmonic_matrix(samples, srate, freq, harmonics = 64):
    waves = []

    for h in range(1, harmonics +1):
        f = freq * h
        f = f if f <srate/2 else 0
        waves.append(W.complex_sinusoid_s(samples, srate, f, 0))

    return np.array(waves)

def cmatrix(samples, srate, freqs, phase =0 ):

    waves = []

    for f in freqs:
        waves.append(W.complex_sinusoid_s(samples, srate,f, phase))

    return np.array(waves)

def dct(cmatrix,signal, **kwargs):
    output = dct_coeff(cmatrix, signal, **kwargs)
    output = dct_amp(output, signal)
    return output

def dct_coeff(cmatrix,signal, **kwargs):
    #i = initial, f = final
    rowi = kwargs.get('rowi', 0)
    rowf = kwargs.get('rowf',cmatrix.shape[0])
    indi = kwargs.get('indi', 0)
    indf = kwargs.get('indf', len(signal))

    sig = signal[indi:indf]
    mat = cmatrix[ rowi:rowf, indi:indf]
    output = np.dot(mat, sig)
    return output

def dct_amp(coeff, signal):
    return np.abs(coeff) /len(signal)