import numpy as np
from .base_instrument import BaseInstrument

class Piano(BaseInstrument):
    """
    A simple piano sound using additive synthesis of harmonics.
    """
    def __init__(self, **adsr_params):
        # Piano has a fast attack and quick decay to zero
        adsr_params.setdefault('attack_s', 0.002)
        adsr_params.setdefault('decay_s', 0.3)
        adsr_params.setdefault('sustain_level', 0.0)
        super().__init__(**adsr_params)
        
        # Harmonic structure (amplitude relative to fundamental)
        self.harmonics = [
            (1.0, 1.0),   # 1st harmonic (fundamental)
            (2.0, 0.4),   # 2nd harmonic
            (3.0, 0.2),   # 3rd harmonic
            (4.0, 0.1),   # 4th harmonic
            (5.0, 0.05),  # 5th harmonic
        ]

    def _generate_wave(self, t, frequencies, sample_rate):
        mixed_wave = np.zeros(len(t))
        
        for freq in frequencies:
            for harmonic_mult, amp_mult in self.harmonics:
                mixed_wave += amp_mult * np.sin(2 * np.pi * (freq * harmonic_mult) * t)
        
        return mixed_wave