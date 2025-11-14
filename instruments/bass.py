import numpy as np
from scipy import signal # For sawtooth wave
from .base_instrument import BaseInstrument

class Bass(BaseInstrument):
    """
    A simple electric bass synthesizer.

    This sound is a mix of a sine wave (for the fundamental 'body')
    and a sawtooth wave (for the bright 'pluck' harmonics).

    The default envelope is set to have a fast attack, a quick
    decay, and a low sustain, simulating a plucked string.
    """
    
    def __init__(self, **adsr_params):
        # Set default envelope parameters for a plucked bass
        # Users can still override this in create_instrument()
        adsr_params.setdefault('attack_s', 0.005) # Very fast attack (5ms)
        adsr_params.setdefault('decay_s', 0.15)   # Quick decay (150ms)
        adsr_params.setdefault('sustain_level', 0.1) # Low sustain (10%)
        
        # Call the parent __init__ with these parameters
        super().__init__(**adsr_params)

    def _generate_wave(self, t, frequencies, sample_rate):
        """
        Generates the raw bass waveform by mixing sine and saw waves.
        """
        mixed_wave = np.zeros(len(t))
        
        for freq in frequencies:
            # Sine wave for the fundamental 'body'
            sine_wave = np.sin(2 * np.pi * freq * t)
            
            # Sawtooth wave for the 'pluck' and harmonics
            saw_wave = signal.sawtooth(2 * np.pi * freq * t)
            
            # Mix them 50/50.
            # This gives it body but also the brightness of a string.
            mixed_wave += 0.5 * sine_wave + 0.5 * saw_wave
            
        return mixed_wave