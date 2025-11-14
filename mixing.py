import numpy as np
import os
from scipy.io.wavfile import write
from music_tools import NoteFrequencies
# FIX: Import BaseInstrument from its new location
from instruments.base_instrument import BaseInstrument

# --- AUDIO MIXER CLASS ---

class AudioMixer:
    """
    Mixes multiple frequencies into a single waveform
    or generates silence.
    """
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    # FIX: Change type hint from Instrument to BaseInstrument
    def get_chord_waveform(self, instrument: BaseInstrument, frequencies: list, duration_s: float, amplitude=0.5):
        """
        Generates a mixed waveform for a list of frequencies
        USING A SPECIFIC INSTRUMENT.
        """
        if not frequencies:
            return self.get_silence_waveform(duration_s)
            
        wave = instrument.get_waveform(
            frequencies=frequencies,
            duration_s=duration_s,
            sample_rate=self.sample_rate,
            amplitude=amplitude
        )
        
        return wave

    def get_silence_waveform(self, duration_s: float):
        """Generates a waveform of zeros (silence)."""
        num_samples = int(self.sample_rate * duration_s)
        return np.zeros(num_samples)

# --- SONG PLAYER CLASS ---

class SongPlayer:
    """
    Sequences notes and chords based on a tempo (BPM)
    to generate a full song waveform.
    """
    
    # FIX: Change type hint from Instrument to BaseInstrument
    def __init__(self, tempo, instrument: BaseInstrument, sample_rate=44100, a4=440.0):
        """
        Initialize the player with a tempo and a default instrument.
        """
        self.tempo = tempo
        self.sample_rate = sample_rate
        self.beat_duration_s = 60.0 / tempo # Duration of one beat
        
        # Internal tools
        self.freq_calc = NoteFrequencies(a4)
        self.mixer = AudioMixer(sample_rate)
        self.instrument = instrument

    def get_note_waveform(self, note_list: list, duration_s: float, amplitude: float):
        """
        Generates the waveform for a single note or chord,
        applying a short fade-out to make it sound distinct.
        """
        # 1. Get frequencies from note names
        frequencies = []
        if note_list: # Check if it's not a rest
            for note_name in note_list:
                freq = self.freq_calc.get_frequency(note_name)
                if freq:
                    frequencies.append(freq)
        
        # 2. Get the base waveform from the mixer, using our instrument
        base_wave = self.mixer.get_chord_waveform(
            self.instrument, frequencies, duration_s, amplitude
        )
        
        # 3. Apply a short fade-out (Release) to prevent clicks
        fade_duration_s = 0.01 # 10ms fade-out
        fade_out_samples = int(self.sample_rate * fade_duration_s)
        
        if fade_out_samples > 0 and len(base_wave) > fade_out_samples:
            # Create a fade-out envelope (linear from 1 to 0)
            fade_out_env = np.linspace(1, 0, fade_out_samples)
            # Apply it to the end of the wave
            base_wave[-fade_out_samples:] *= fade_out_env
            
        return base_wave

    def generate_song_waveform(self, song_data: list, amplitude=0.5):
        """
        Generates the full song waveform by sequencing notes.
        """
        all_wave_chunks = []
        print(f"Generating song with {self.instrument.__class__.__name__}...")
        for note_list, num_beats in song_data:
            duration_s = self.beat_duration_s * num_beats
            chunk = self.get_note_waveform(note_list, duration_s, amplitude)
            all_wave_chunks.append(chunk)
            
        final_waveform = np.concatenate(all_wave_chunks)
        print("Song generation complete.")
        return final_waveform

# --- MULTI-TRACK MIXER CLASS ---

class MultiTrackMixer:
    """
    Mixes multiple, pre-generated audio tracks (waveforms) into one.
    Handles different track lengths, applies individual track volumes,
    and performs final normalization.
    """
    
    def __init__(self, master_amplitude=0.8):
        self.master_amplitude = np.clip(master_amplitude, 0.0, 1.0)

    def mix_tracks(self, tracks_with_volumes: list):
        """
        Mixes a list of tracks, each with a specified volume.
        """
        if not tracks_with_volumes:
            print("Warning: No tracks to mix.")
            return np.array([])
            
        try:
            max_len = max(len(t[0]) for t in tracks_with_volumes)
        except (TypeError, IndexError):
            print("Error: 'tracks_with_volumes' must be a list of (waveform, volume) tuples.")
            return np.array([])

        master_track = np.zeros(max_len)
        
        for track_wave, volume in tracks_with_volumes:
            if track_wave is None or len(track_wave) == 0:
                continue
            scaled_track = track_wave * max(0.0, volume)
            master_track[:len(scaled_track)] += scaled_track
            
        max_val = np.max(np.abs(master_track))
        if max_val > 1.0:
            print(f"Info: Mix exceeded 1.0 (max val: {max_val:.2f}), normalizing.")
            master_track /= max_val
            
        final_mix = np.clip(master_track * self.master_amplitude, -1.0, 1.0)
        return final_mix

# --- Utility Functions ---

def normalize_to_16bit(waveform):
    """Converts float waveform (-1.0 to 1.0) to 16-bit int."""
    waveform_int = np.int16(waveform * 32767)
    return waveform_int

def save_wav(filename, sample_rate, waveform_int):
    """Saves the 16-bit integer waveform to a .wav file."""
    if not os.path.isabs(filename):
        os.makedirs("sounds", exist_ok=True)
        filename = os.path.join("sounds", filename)
    write(filename, sample_rate, waveform_int)
    print(f"✅ Successfully saved '{filename}'")