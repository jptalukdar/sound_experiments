import numpy as np
from .base_instrument import BaseInstrument
from music_tools import NoteFrequencies

class Drums(BaseInstrument):
    """
    A simple drum machine instrument.
    Maps note names to percussive sounds (kick, snare, hat, tom).
    Note frequencies are used to identify *which* drum to play.
    """
    
    def __init__(self, **adsr_params):
        # We set the base envelope to be "flat" because we
        # will generate our own per-drum envelopes.
        adsr_params.setdefault('attack_s', 0.0)
        adsr_params.setdefault('decay_s', 0.0)
        adsr_params.setdefault('sustain_level', 1.0)
        super().__init__(**adsr_params)
        
        # We need our own frequency calculator to map
        # incoming frequencies back to their note names.
        self.freq_calc = NoteFrequencies()
        
        # Define the note-to-frequency mappings
        self.note_map = {
            'kick': self.freq_calc.get_frequency('C4'),
            'snare': self.freq_calc.get_frequency('D4'),
            'tom': self.freq_calc.get_frequency('F4'),
            'hat': self.freq_calc.get_frequency('G4')
        }

    def _create_envelope(self, attack_s, decay_s, sustain_level, num_samples, sample_rate):
        """Helper to create a per-note ADS envelope."""
        env = np.zeros(num_samples)
        
        attack_samples = int(sample_rate * attack_s)
        decay_samples = int(sample_rate * decay_s)
        
        attack_samples = min(attack_samples, num_samples)
        decay_samples = min(decay_samples, num_samples - attack_samples)
        sustain_samples = num_samples - attack_samples - decay_samples

        if attack_samples > 0:
            env[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        if decay_samples > 0:
            env[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain_level, decay_samples)
            
        if sustain_samples > 0:
            env[attack_samples + decay_samples:] = sustain_level
            
        return env

    def _create_kick(self, t, sample_rate):
        """A simple kick: low sine wave with a pitch drop."""
        num_samples = len(t)
        # Generate a short, fast envelope
        env = self._create_envelope(0.001, 0.15, 0.0, num_samples, sample_rate)
        
        # Pitch envelope (120Hz down to 40Hz)
        freq_env = np.linspace(120, 40, num_samples)
        
        # A simple sine wave oscillator whose frequency changes over time
        # We calculate the phase by taking the cumulative sum of frequency
        phase = np.cumsum(2 * np.pi * freq_env / sample_rate)
        wave = np.sin(phase)
        return wave * env

    def _create_snare(self, t, sample_rate):
        """A simple snare: white noise + a sharp sine "pop"."""
        num_samples = len(t)
        env = self._create_envelope(0.001, 0.1, 0.0, num_samples, sample_rate)
        
        # White noise component
        noise = np.random.uniform(-0.5, 0.5, num_samples)
        
        # "Body" component (a short sine pop)
        body = 0.5 * np.sin(2 * np.pi * 200 * t)
        
        return (noise + body) * env

    def _create_hat(self, t, sample_rate):
        """A simple hi-hat: filtered white noise."""
        num_samples = len(t)
        env = self._create_envelope(0.001, 0.05, 0.0, num_samples, sample_rate)
        
        # "Bright" noise (cubing it emphasizes peaks)
        noise = np.random.uniform(-1, 1, num_samples) ** 3
        return noise * env

    def _create_tom(self, t, sample_rate):
        """A simple tom: like a kick but higher pitch."""
        num_samples = len(t)
        env = self._create_envelope(0.001, 0.2, 0.0, num_samples, sample_rate)
        
        # Pitch envelope (200Hz down to 100Hz)
        freq_env = np.linspace(200, 100, num_samples)
        phase = np.cumsum(2 * np.pi * freq_env / sample_rate)
        wave = np.sin(phase)
        return wave * env

    def _generate_wave(self, t, frequencies, sample_rate):
        """
        Mixes drum sounds based on the incoming frequencies.
        """
        mixed_wave = np.zeros(len(t))
        
        for freq in frequencies:
            # Compare frequencies to see which drum to trigger
            if np.isclose(freq, self.note_map['kick']):
                mixed_wave += self._create_kick(t, sample_rate)
            elif np.isclose(freq, self.note_map['snare']):
                mixed_wave += self._create_snare(t, sample_rate)
            elif np.isclose(freq, self.note_map['hat']):
                mixed_wave += self._create_hat(t, sample_rate)
            elif np.isclose(freq, self.note_map['tom']):
                mixed_wave += self._create_tom(t, sample_rate)
                
        return mixed_wave