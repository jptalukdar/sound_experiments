import numpy as np
from scipy import signal
from .base_instrument import BaseInstrument # Relative import

class Sine(BaseInstrument):
    """A simple, pure sine wave oscillator."""
    def _generate_wave(self, t, frequencies, sample_rate):
        mixed_wave = np.zeros(len(t))
        for freq in frequencies:
            mixed_wave += np.sin(2 * np.pi * freq * t)
        return mixed_wave

class Square(BaseInstrument):
    """A square wave oscillator."""
    def _generate_wave(self, t, frequencies, sample_rate):
        mixed_wave = np.zeros(len(t))
        for freq in frequencies:
            mixed_wave += signal.square(2 * np.pi * freq * t)
        return mixed_wave

class Sawtooth(BaseInstrument):
    """A sawtooth wave oscillator."""
    def _generate_wave(self, t, frequencies, sample_rate):
        mixed_wave = np.zeros(len(t))
        for freq in frequencies:
            # Use signal.sawtooth for an upward-ramping saw
            mixed_wave += signal.sawtooth(2 * np.pi * freq * t)
        return mixed_wave