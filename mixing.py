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
    
    # --- MODIFIED __init__ ---
    def __init__(self, tempo, instrument: BaseInstrument, time_signature="4/4", sample_rate=44100, a4=440.0):
        """
        Initialize the player with a tempo, instrument, and time signature.
        
        Args:
            tempo (int): Beats Per Minute (relative to the time signature's beat unit).
            instrument (BaseInstrument): The instrument to play.
            time_signature (str): e.g., "4/4", "3/4", "6/8".
        """
        self.tempo = tempo
        self.instrument = instrument
        self.sample_rate = sample_rate
        
        # Parse time signature
        try:
            parts = time_signature.split('/')
            self.beats_per_measure = int(parts[0])
            self.beat_unit = int(parts[1]) # e.g., 4 for quarter, 8 for eighth
        except Exception:
            print(f"Warning: Invalid time signature '{time_signature}'. Defaulting to 4/4.")
            self.beats_per_measure = 4
            self.beat_unit = 4
            
        # --- NEW DURATION LOGIC ---
        # Calculate the duration of a single "beat" (as defined by tempo and time_sig)
        # e.g., if 6/8 and 180 BPM, this is the duration of one 8th note.
        self.base_beat_duration_s = 60.0 / self.tempo
        
        # Calculate the duration of a single quarter note. This is our
        # standard unit for composing.
        # (beat_unit / 4.0) is the multiplier.
        # e.g., 6/8: (8 / 4.0) = 2.0. A quarter note is 2x an 8th note beat.
        # e.g., 4/4: (4 / 4.0) = 1.0. A quarter note is 1x a quarter note beat.
        # e.g., 2/2: (2 / 4.0) = 0.5. A quarter note is 0.5x a half note beat.
        self.quarter_note_duration_s = self.base_beat_duration_s * (self.beat_unit / 4.0)

        # Internal tools
        self.freq_calc = NoteFrequencies(a4)
        self.mixer = AudioMixer(sample_rate)

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
        
        # 3. Apply a short fade-out (Release)
        fade_duration_s = min(duration_s * 0.05, 0.01) # 10ms or 5%, whichever is shorter
        fade_out_samples = int(self.sample_rate * fade_duration_s)

        if fade_out_samples > 0 and len(base_wave) > fade_out_samples:
            fade_envelope = np.linspace(1.0, 0.0, fade_out_samples)
            base_wave[-fade_out_samples:] *= fade_envelope
            
        return base_wave

    def generate_song_waveform(self, song_data: list, amplitude=0.5):
        """
        Generates the full song waveform from song data.
        
        The 'num_beats' in song_data is *always* relative to a
        quarter note (1.0 = quarter note, 0.5 = 8th note, etc.)
        """
        all_wave_chunks = []
        
        print(f"Generating song with {self.instrument.__class__.__name__} ({self.beats_per_measure}/{self.beat_unit})...")
        for note_list, num_beats in song_data:
            
            # --- MODIFIED DURATION CALCULATION ---
            # Calculate duration based on our standard quarter note length
            duration_s = self.quarter_note_duration_s * num_beats
            
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