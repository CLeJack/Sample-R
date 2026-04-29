import numpy as np
import re

# These constants generate C0 up to C8

REFFREQ = 440; #(Hz) concert tuning
SEMITONE =np.power(2, 1.0 / 12.0); #12 Tone equal temperament
OCTAVESIZE = 12

LOWEXP = -57
HIGHEXP = 50 


import numpy as np



def get_freqs(ref_freq =REFFREQ, semitone=SEMITONE, low_exp=LOWEXP, high_exp=HIGHEXP):
    # freq = fundamental * SEMITONE^exponent
    return np.array([ref_freq * semitone ** n for n in range(low_exp, high_exp + 1)])

def get_index(freq, refFreq, semitone, minExponent):
    # the lowest note of consideration (i.e. C0_exponent) will be considered 0
    # this can then be used to lookup values from the note table by note name of frequency

    # reverse calculate_notes()
    semitone_to_exp = freq / refFreq

    exponent = np.log(semitone_to_exp) / np.log(semitone)

    # can't go below the lowest exponent / C0
    exponent = max(minExponent, exponent)
    offset = int(0.5 + exponent - minExponent)  # round up to the nearest exponent
    return offset

# integer based pitch class
def get_class_index(freq):

    offset = get_index(freq)
    index = offset % 12
    return index

def pitch_class_to_freq(text):

    output = 0
    regex = '([ABCDEFGabcdefg])([s#b]{0,1})([1-8])'
    results = re.search(regex,text)
    if not(results is None):
    
        pitch_class, accidental, octave = results.groups()
        
        # Treat C0 approx 16hz as lowest tonal frequency 
        # this is associated with index -57 based on the note_freq formula

        indices = [-57 + i for i in [0,2,4,5,7,9,11]] # All pitch classes from C0 to A0
        notes = 'C,D,E,F,G,A,B'.split(',')
        ind_map = {k:v for k,v in zip(notes,indices)}
        index = ind_map[pitch_class]
        offset = 0
        if accidental != '':
            offset = -1 if accidental == 'b' else 1

        n = (index + offset) + 12 * int(octave)
        
        output = REFFREQ * SEMITONE ** n
        print(f"Detected pitch class {pitch_class} {accidental} {octave} | Freq: {output}\n")

    else:
        print(f"Could not determine pitch class from {text}")
    
    return output