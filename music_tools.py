import re

class NoteFrequencies:
    """
    Calculates musical note frequencies based on a reference pitch (default A4=440Hz)
    using the 12-tone equal temperament system.
    """
    
    def __init__(self, a4=440.0):
        self.a4 = a4
        self.twelfth_root_of_2 = 2**(1/12)
        
        self.note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        
        self.semitones_a4 = self.note_map['A'] + 4 * 12 # 57
        self.note_regex = re.compile(r'([A-G])([#b]?)(\d)')

    def get_frequency(self, note_name):
        """Returns the frequency of a given note (e.g., "A4", "C#5")."""
        match = self.note_regex.match(note_name.strip())
        
        if not match:
            print(f"Error: Invalid note format '{note_name}'.")
            return None
            
        note_letter, accidental, octave_str = match.groups()
        
        try:
            note_base_name = note_letter + accidental
            semitone_base = self.note_map[note_base_name]
            octave = int(octave_str)
            
            target_semitone_num = semitone_base + octave * 12
            n = target_semitone_num - self.semitones_a4
            frequency = self.a4 * (self.twelfth_root_of_2 ** n)
            
            return frequency
            
        except KeyError:
            print(f"Error: Invalid note name '{note_base_name}'.")
            return None

# --- NEW CHORD CLASS ---

class Chord:
    """
    Uses a NoteFrequencies object to calculate the frequencies
    of all notes in a chord based on a root note and quality.
    """
    
    def __init__(self, freq_calculator: NoteFrequencies):
        """
        Initializes the Chord builder.
        
        Args:
            freq_calculator: An instantiated NoteFrequencies object.
        """
        self.freq_calc = freq_calculator
        self.twelfth_root_of_2 = 2**(1/12)
        
        # Define chord "recipes" by their semitone intervals from the root
        self.chord_intervals = {
            # Triads
            'major': [0, 4, 7],
            'minor': [0, 3, 7],
            'diminished': [0, 3, 6],
            'augmented': [0, 4, 8],
            
            # Sevenths
            'major7': [0, 4, 7, 11],
            'minor7': [0, 3, 7, 10],
            'dominant7': [0, 4, 7, 10],
        }

    def get_frequencies(self, root_note: str, quality: str):
        """
        Returns a list of frequencies for the specified chord.
        
        Args:
            root_note (str): The root note (e.g., "C4", "A3").
            quality (str): The chord quality (e.g., "major", "minor7").
            
        Returns:
            list[float]: A list of frequencies, or an empty list on failure.
        """
        # 1. Get the root frequency
        root_freq = self.freq_calc.get_frequency(root_note)
        if root_freq is None:
            print(f"Error: Invalid root note '{root_note}'")
            return []
            
        # 2. Get the chord's interval "recipe"
        intervals = self.chord_intervals.get(quality)
        if intervals is None:
            print(f"Error: Invalid chord quality '{quality}'.")
            print(f"Supported qualities: {list(self.chord_intervals.keys())}")
            return []
            
        # 3. Calculate each frequency based on the root
        # f_note = f_root * (2^(1/12))^n
        chord_freqs = [root_freq * (self.twelfth_root_of_2 ** n) for n in intervals]
        
        return chord_freqs