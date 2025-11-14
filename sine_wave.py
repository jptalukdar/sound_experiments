import numpy as np
from scipy.io.wavfile import write
from scipy import signal # Used for sawtooth wave example

## 1. Core Audio Generation Functions
# ==================================
# (These functions do not need to be changed; they
# already support 2D arrays for stereo)

def generate_audio_file(filename, duration_s, sample_rate, wave_function, **wave_params):
    """
    Generates a .wav file from a given user-defined wave function.
    Handles both mono (1D) and stereo (2D) outputs from the wave_function.
    """
    print(f"Generating '{filename}'...")
    
    # 1. Generate Time Array
    num_samples = int(sample_rate * duration_s)
    t = np.linspace(0., duration_s, num_samples, endpoint=False)
    
    # 2. Generate the Waveform
    # This will be 1D for mono or 2D for stereo, based on the function
    waveform_float = wave_function(t, **wave_params)
    
    # 3. Normalize and Convert to 16-bit
    waveform_int = normalize_to_16bit(waveform_float)
    
    # 4. Write to File
    save_wav(filename, sample_rate, waveform_int)

def normalize_to_16bit(waveform):
    """
    Normalizes a float waveform (-1.0 to 1.0) to 16-bit integer 
    (-32768 to 32767) for .wav file storage.
    Works for both 1D (mono) and 2D (stereo) arrays.
    """
    waveform_clipped = np.clip(waveform, -1.0, 1.0)
    waveform_int = np.int16(waveform_clipped * 32767)
    return waveform_int

def save_wav(filename, sample_rate, waveform_int):
    """
    Saves the 16-bit integer waveform to a .wav file.
    Automatically saves as stereo if waveform_int is 2D.
    """
    write(filename, sample_rate, waveform_int)
    print(f"✅ Successfully saved '{filename}'")


## 2. User-Definable Wave Functions (f(t) -> y)
# ===========================================

def sine_wave(t, frequency, amplitude=0.5):
    """A simple mono sine wave."""
    return amplitude * np.sin(2 * np.pi * frequency * t)

def simple_chord(t, freq1, freq2, amplitude=0.5):
    """A complex mono wave: two sine waves added together."""
    wave1 = (amplitude / 2) * np.sin(2 * np.pi * freq1 * t)
    wave2 = (amplitude / 2) * np.sin(2 * np.pi * freq2 * t)
    return wave1 + wave2

def sawtooth_wave(t, frequency, amplitude=0.5):
    """A non-sinusoidal mono wave (sawtooth)."""
    return amplitude * signal.sawtooth(2 * np.pi * frequency * t)

# --- NEW BINAURAL FUNCTION ---
def binaural_beat(t, base_frequency, beat_frequency, amplitude=0.5):
    """
    Generates a stereo binaural beat.
    The 'base_frequency' is sent to the left ear.
    The 'base_frequency + beat_frequency' is sent to the right ear.
    
    Returns:
        A 2D NumPy array of shape (num_samples, 2).
    """
    # 1. Define left and right frequencies
    freq_left = base_frequency
    freq_right = base_frequency + beat_frequency
    
    # 2. Generate separate waves for each channel
    wave_left = amplitude * np.sin(2 * np.pi * freq_left * t)
    wave_right = amplitude * np.sin(2 * np.pi * freq_right * t)
    
    # 3. Stack them into a 2-column (stereo) array
    waveform_stereo = np.stack([wave_left, wave_right], axis=1)
    
    return waveform_stereo


## 3. Main Execution (Driver Code)
# ===============================

if __name__ == "__main__":
    # Define global audio parameters
    SAMPLE_RATE = 44100
    DURATION = 5.0 # Longer duration to hear the beat

    print("--- Starting Audio Generation ---")

    # Example 1: Simple mono sine wave (as before)
    generate_audio_file(
        filename='sine_440.wav',
        duration_s=DURATION,
        sample_rate=SAMPLE_RATE,
        wave_function=sine_wave,
        frequency=440,
        amplitude=0.5
    )
    
    # --- NEW BINAURAL EXAMPLE ---
    # This will create a 10 Hz "Alpha" wave beat, based on a 440 Hz tone.
    # Remember to listen with headphones!
    generate_audio_file(
        filename='binaural_10hz_beat.wav',
        duration_s=DURATION,
        sample_rate=SAMPLE_RATE,
        wave_function=binaural_beat,
        # --- wave_params start here ---
        base_frequency=440,  # 440 Hz in left ear
        beat_frequency=10,   # 450 Hz in right ear (440 + 10)
        amplitude=0.5
    )

    print("--- All files generated. ---")