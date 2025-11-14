import re
from music_tools import NoteFrequencies

class NoteAliases:
    """
    A class to hold aliases for notes and chords to make
    song composition more readable.
    
    Provides case-insensitive .get() method for parsers.
    """
    def __init__(self):
        # REST is a universal alias
        self.add_notes(REST=[])

    def add_notes(self, **kwargs):
        """Adds single notes as lists. e.g., C4=['C4']"""
        for name, note_val in kwargs.items():
            if not isinstance(note_val, list):
                note_val = [note_val]
            setattr(self, name, note_val)

    def add_chords(self, **kwargs):
        """Adds chords (lists of notes). e.g., C_MAJOR=['C4', 'E4', 'G4']"""
        # This is functionally the same as add_notes
        for name, chord_val in kwargs.items():
            setattr(self, name, chord_val)
            
    def get(self, name):
        """Gets an alias by name, case-insensitive."""
        # Check attributes
        for attr in dir(self):
            if attr.lower() == name.lower():
                return getattr(self, attr)
        return None

def _create_prefilled_aliases():
    """
    Internal function to generate a NoteAliases object
    pre-filled with standard notes and chords.
    """
    aliases = NoteAliases()
    
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_names_for_chords = [] # (note_str, octave, full_note_name)
    
    # --- 1. Add all notes from C2 to B5 ---
    for octave in range(2, 6): # Octaves 2, 3, 4, 5
        for note in notes:
            note_name = f"{note}{octave}"
            # Sanitize name for attribute (C#4 -> Csharp4)
            attr_name = note_name.replace('#', 'sharp')
            aliases.add_notes(**{attr_name: [note_name]})
            note_names_for_chords.append((note, octave, note_name))

    # --- 2. Add standard chords ---
    # We need a freq calc to build the chord note names
    freq_calc_temp = NoteFrequencies()
    # A map of semitone offset to note name
    semitone_map = {v: k for k, v in freq_calc_temp.note_map.items() if '#' not in k}
    semitone_map[1] = 'C#'
    semitone_map[3] = 'D#'
    semitone_map[6] = 'F#'
    semitone_map[8] = 'G#'
    semitone_map[10] = 'A#'
    
    chord_recipes = {
        'MAJOR': [0, 4, 7],
        'MINOR': [0, 3, 7],
        'DIM': [0, 3, 6],   # diminished
        'AUG': [0, 4, 8],   # augmented
    }
    
    # Helper to get note name from base semitone + offset
    def get_note_from_semitone(base_semi, octave, offset):
        new_semi = (base_semi + offset) % 12
        new_octave = octave + (base_semi + offset) // 12
        note_letter = semitone_map[new_semi]
        return f"{note_letter}{new_octave}"

    for note, octave, root_note_name in note_names_for_chords:
        base_semitone = freq_calc_temp.note_map.get(note)
        if base_semitone is None:
            continue
            
        for recipe_name, recipe_intervals in chord_recipes.items():
            chord_notes = [
                get_note_from_semitone(base_semitone, octave, interval)
                for interval in recipe_intervals
            ]
            
            # e.g., C4_MAJOR
            attr_name = f"{root_note_name.replace('#', 'sharp')}_{recipe_name}"
            aliases.add_chords(**{attr_name: chord_notes})
            
            # Add default octave (4) alias, e.g. C_MAJOR
            if octave == 4:
                attr_name_default = f"{note.replace('#', 'sharp')}_{recipe_name}"
                if not hasattr(aliases, attr_name_default):
                    aliases.add_chords(**{attr_name_default: chord_notes})

    # --- 3. Add Drum Aliases ---
    aliases.add_chords(
        KICK = ['C4'],
        SNARE = ['D4'],
        HAT = ['G4'],
        TOM = ['F4'],
        KICK_HAT = ['C4', 'G4'],
        SNARE_HAT = ['D4', 'G4']
    )

    return aliases

# --- Create the single, pre-filled instance ---
# This is imported by other modules (e.g., main.py, song_parser.py)
aliases = _create_prefilled_aliases()