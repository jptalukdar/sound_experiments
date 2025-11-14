import numpy as np
import os
from scipy.io.wavfile import write

# --- Project Imports ---
# We need the factory to find instruments,
# aliases for notes, and SongPlayer to generate audio.
from sound_design import InstrumentFactory
from composition_tools import aliases
from mixing import SongPlayer

# --- Config ---
SAMPLE_RATE = 44100
TEMPO = 120 # 120 BPM for all test clips

# --- Utility Functions (Copied from mixing.py) ---
# We copy these to change the save directory to 'samples/'
# without modifying the main 'mixing.py' file.

def normalize_to_16bit(waveform):
    """Converts float waveform (-1.0 to 1.0) to 16-bit int."""
    waveform_int = np.int16(waveform * 32767)
    return waveform_int

def save_wav_sample(filename, sample_rate, waveform_int):
    """Saves the 16-bit integer waveform to a .wav file in the 'samples/' directory."""
    output_dir = "samples" # Changed from 'sounds'
    if not os.path.isabs(filename):
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, filename)
    write(filename, sample_rate, waveform_int)
    print(f"✅ Successfully saved sample: '{filename}'")

# --- Test Riffs ---
# Note durations are in "quarter notes" (1.0 = quarter, 0.5 = 8th)
# This assumes your SongPlayer uses the time_signature logic.

# A simple arpeggio for tonal instruments (C, E, G, C5, C-Major Chord)
TONAL_RIFF = [
    (aliases.C4, 0.5),    # 8th note
    (aliases.E4, 0.5),    # 8th note
    (aliases.G4, 0.5),    # 8th note
    (aliases.C5, 1.0),    # Quarter note
    (aliases.REST, 0.5),  # 8th rest
    (aliases.C_MAJOR, 1.0), # Quarter note chord
]

# A simple beat for the drum instrument
# We must add these aliases before using them
aliases.add_chords(
    KICK = ['C4'],
    SNARE = ['D4'],
    HAT = ['G4'],
    TOM = ['F4']
)
DRUM_RIFF = [
    (aliases.KICK, 0.5),  # 8th note
    (aliases.HAT, 0.5),
    (aliases.SNARE, 0.5),
    (aliases.HAT, 0.5),
    (aliases.KICK, 0.5),
    (aliases.TOM, 0.5),
    (aliases.SNARE, 0.5),
    (aliases.HAT, 0.5),
]

# --- The Tester Class ---

class SoundTester:
    """
    Generates a .wav sample for each instrument plugin found.
    """
    def __init__(self, sample_rate=SAMPLE_RATE, tempo=TEMPO):
        print("Initializing Sound Tester...")
        self.factory = InstrumentFactory()
        self.sample_rate = sample_rate
        self.tempo = tempo
        print("-" * 30)
        print(f"Found {len(self.factory.loaded_plugins)} instruments to test.")
        print("-" * 30)

    def generate_samples(self):
        """
        Loops through all loaded instruments and generates a sample file.
        """
        if not self.factory.loaded_plugins:
            print("No instruments found in 'instruments/' directory.")
            return

        for name in self.factory.loaded_plugins.keys():
            print(f"\n--- Testing: {name} ---")
            try:
                instrument = self.factory.create_instrument(name)
                
                # Select the correct riff for the instrument
                if name == 'drums':
                    riff = DRUM_RIFF
                else:
                    riff = TONAL_RIFF
                
                # Use SongPlayer to generate the test
                player = SongPlayer(
                    tempo=self.tempo,
                    instrument=instrument,
                    time_signature="4/4", # Use 4/4 as the test standard
                    sample_rate=self.sample_rate
                )
                
                # Generate the waveform
                waveform = player.generate_song_waveform(riff, amplitude=0.7)
                
                # Save the file
                waveform_16bit = normalize_to_16bit(waveform)
                save_wav_sample(f"{name}_sample.wav", self.sample_rate, waveform_16bit)
                
            except Exception as e:
                print(f"FAILED to generate sample for '{name}': {e}")
                import traceback
                traceback.print_exc()

# --- Main execution ---
if __name__ == "__main__":
    """
    This script will generate a sample .wav file for every
    instrument plugin it finds in the 'instruments/' folder
    and save them to the 'samples/' folder.
    """
    tester = SoundTester()
    tester.generate_samples()
    print("\n--- Sound testing complete. ---")
    print("Check the 'samples/' directory for output files.")
