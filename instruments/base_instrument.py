import numpy as np
import abc # Abstract Base Class

class BaseInstrument(abc.ABC):
    """
    Abstract base class for all instrument plugins.
    Defines the required interface for an instrument.
    """
    
    def __init__(self, attack_s=0.01, decay_s=0.0, sustain_level=1.0):
        """
        Initializes the instrument with its envelope parameters.
        """
        self.attack_s = attack_s
        self.decay_s = decay_s
        self.sustain_level = sustain_level
        
    def apply_ads_envelope(self, waveform, duration_s, sample_rate):
        """
        Applies an Attack-Decay-Sustain (ADS) envelope to a waveform.
        (The "Release" is handled by SongPlayer's note fade-out)
        """
        num_samples = len(waveform)
        if num_samples == 0:
            return waveform
            
        attack_samples = int(sample_rate * self.attack_s)
        decay_samples = int(sample_rate * self.decay_s)
        
        # Ensure envelope segments don't exceed total duration
        attack_samples = min(attack_samples, num_samples)
        decay_samples = min(decay_samples, num_samples - attack_samples)
        sustain_samples = num_samples - attack_samples - decay_samples

        if attack_samples > 0:
            attack_env = np.linspace(0, 1, attack_samples)
            waveform[:attack_samples] *= attack_env
        
        if decay_samples > 0:
            decay_env = np.linspace(1, self.sustain_level, decay_samples)
            waveform[attack_samples:attack_samples + decay_samples] *= decay_env
            
        if sustain_samples > 0:
            waveform[attack_samples + decay_samples:] *= self.sustain_level
            
        return waveform

    @abc.abstractmethod
    def _generate_wave(self, t, frequencies, sample_rate):
        """
        PLUGIN'S CORE LOGIC: Must be overridden by the child class.
        Generates the raw, un-enveloped waveform.
        
        Args:
            t (np.array): The time array.
            frequencies (list): List of frequencies to play.
            sample_rate (int): The sample rate.
            
        Returns:
            np.array: The raw waveform.
        """
        pass

    def get_waveform(self, frequencies: list, duration_s: float, sample_rate: int, amplitude: float):
        """
        Public method to get the final, enveloped waveform.
        This method should not be overridden.
        """
        num_samples = int(sample_rate * duration_s)
        t = np.linspace(0., duration_s, num_samples, endpoint=False)
        
        if not frequencies:
            return np.zeros(num_samples)

        # 1. Call the plugin's specific generator
        raw_wave = self._generate_wave(t, frequencies, sample_rate)
        
        # 2. Normalize and apply amplitude
        max_val = np.max(np.abs(raw_wave))
        if max_val > 0:
            raw_wave /= max_val
        raw_wave *= amplitude

        # 3. Apply the ADS envelope
        enveloped_wave = self.apply_ads_envelope(raw_wave, duration_s, sample_rate)
        
        return enveloped_wave