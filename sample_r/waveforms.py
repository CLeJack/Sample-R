import numpy as np

def time_input(time, srate):
    return np.arange(0, time, 1/srate)

def sample_input(samples, srate):
    time = samples/srate
    return np.arange(0, time, 1/srate)

def sinusoid(x, frequency, phase = 0, amplitude = 1):
    return amplitude * np.sin(2*np.pi*frequency*x  + phase*np.pi/180)

def sinusoid_t(time, srate, frequency, phase = 0, amplitude = 1):
    x = time_input(time, srate)
    return sinusoid(x, frequency, phase, amplitude)

def sinusoid_s(samples,srate, frequency, phase = 0, amplitude = 1):
    x = sample_input(samples, srate)
    return sinusoid(x, frequency, phase, amplitude)

def complex_sinusoid(x, frequency, phase = 0, amplitude = 1):
    omega = 2 * np.pi * frequency
    theta = phase*np.pi/180
    return amplitude * np.exp(1j*(omega*x + theta))

def complex_sinusoid_s(samples, srate, frequency, phase = 0, amplitude = 1):
    x = sample_input(samples, srate)
    return complex_sinusoid(x,frequency, phase, amplitude)