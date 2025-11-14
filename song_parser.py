import re

# --- Project Imports ---
from sound_design import InstrumentFactory
from mixing import SongPlayer, MultiTrackMixer, save_wav, normalize_to_16bit
from composition_tools import aliases # Import the pre-filled aliases object

class SongParser:
    """
    Parses a .song text file and uses the synthesizer framework
    to build the final .wav file.
    
    The .song format supports:
    - Global settings (TEMPO, SAMPLE_RATE, etc.)
    - Track definitions ([TRACK: ...])
    - Track settings (INSTRUMENT, VOLUME, TIME_SIGNATURE)
    - Note data (aliases + duration, duration defaults to 1.0)
    - Repeat commands ([REPEAT: ...])
    - Comments (# ...)
    """
    
    def __init__(self, input_file):
        """
        Initializes the parser.
        
        Args:
            input_file (str): The path to the .song file to parse.
        """
        self.input_file = input_file
        self.factory = InstrumentFactory()
        self.aliases = aliases # Use the pre-filled aliases
        
        # Parsed data
        self.global_settings = {
            'TEMPO': 120,
            'SAMPLE_RATE': 44100,
            'MASTER_AMPLITUDE': 0.7,
            'OUTPUT_FILE': 'output.wav'
        }
        self.tracks = [] # List of track dictionaries

    def build_song(self):
        """
        Public method to parse the file and build the song.
        """
        try:
            print(f"--- Parsing {self.input_file} ---")
            self._parse_file()
            print("--- Parsing complete ---")
            
            print("\n--- Building Tracks ---")
            self._build_tracks()
            print("--- Build complete ---")
            
        except Exception as e:
            print(f"An error occurred during song building: {e}")
            import traceback
            traceback.print_exc()

    def _parse_file(self):
        """
        Internal method. Reads and parses the .song file line by line.
        """
        current_track = None
        
        with open(self.input_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # --- Parse [TRACK: name] ---
                if line.startswith('[TRACK:'):
                    track_name = line[7:-1].strip()
                    current_track = {
                        'name': track_name,
                        'settings': {},
                        'data': []
                    }
                    self.tracks.append(current_track)
                    continue
                
                # --- Parse [REPEAT: n] ---
                if line.startswith('[REPEAT:'):
                    if current_track is None:
                        print("Warning: [REPEAT] command found outside of a track. Ignoring.")
                        continue
                    try:
                        repeat_count = int(line[8:-1].strip())
                        # Get all note data *above* the repeat command
                        # This finds the last [TRACK] or [REPEAT] entry and repeats from there.
                        # For simplicity, we'll just repeat the current data block.
                        original_data = list(current_track['data'])
                        for _ in range(repeat_count):
                            current_track['data'].extend(original_data)
                    except ValueError:
                        print(f"Warning: Invalid REPEAT value in line: {line}. Ignoring.")
                    continue

                # --- Parse Settings (TEMPO: 120, INSTRUMENT: piano) ---
                if ':' in line:
                    key, val = line.split(':', 1)
                    key = key.strip().upper()
                    val = val.strip()
                    
                    if current_track:
                        # This is a track setting
                        current_track['settings'][key] = val
                    else:
                        # This is a global setting
                        self.global_settings[key] = val
                    continue

                # --- Parse Note Data (C4, or C4 1.0, or KICK HAT 0.5) ---
                if current_track:
                    parts = line.split()
                    if not parts:
                        continue
                        
                    try:
                        # --- UPDATED LOGIC ---
                        try:
                            # Try to parse the last part as a float
                            duration = float(parts[-1])
                            note_parts = parts[:-1] # All other parts are notes
                        except ValueError:
                            # Failed: Last part is not a float.
                            # Assume default duration of 1.0 and all parts are notes.
                            duration = 1.0
                            note_parts = parts
                        # --- END UPDATED LOGIC ---

                        if not note_parts:
                            print(f"Warning: Line has duration but no notes: '{line}'. Ignoring.")
                            continue

                        note_list = []
                        for note_alias in note_parts:
                            notes = self.aliases.get(note_alias)
                            if notes is not None:
                                note_list.extend(notes)
                            else:
                                print(f"Warning: Unknown alias '{note_alias}' in track '{current_track['name']}'. Ignoring.")
                        
                        current_track['data'].append((note_list, duration))
                        
                    except Exception as e:
                        # General catch-all for any other parsing error on the line
                        print(f"Warning: Invalid note data format in line: '{line}'. Ignoring. Error: {e}")
                
    def _build_tracks(self):
        """
        Internal method. Uses the parsed data to generate
        waveforms and mix the final song.
        """
        # Get global settings
        try:
            tempo = int(self.global_settings['TEMPO'])
            sample_rate = int(self.global_settings['SAMPLE_RATE'])
            master_amplitude = float(self.global_settings['MASTER_AMPLITUDE'])
            output_file = self.global_settings['OUTPUT_FILE']
        except (ValueError, KeyError) as e:
            print(f"Error: Missing or invalid global setting: {e}")
            return

        generated_tracks = [] # To hold (waveform, volume) tuples
        
        for track in self.tracks:
            try:
                # Get track settings
                name = track['name']
                settings = track['settings']
                data = track['data']
                
                instrument_name = settings.get('INSTRUMENT', 'sine')
                volume = float(settings.get('VOLUME', 0.5))
                time_sig = settings.get('TIME_SIGNATURE', '4/4')
                
                print(f"Generating track: '{name}' (Instrument: {instrument_name}, Volume: {volume})")

                # Create instrument
                instrument = self.factory.create_instrument(instrument_name)
                
                # Create player
                player = SongPlayer(
                    tempo=tempo,
                    instrument=instrument,
                    time_signature=time_sig,
                    sample_rate=sample_rate
                )
                
                # Generate wave
                wave = player.generate_song_waveform(data, amplitude=1.0) # Full amplitude, will be scaled by mixer
                generated_tracks.append((wave, volume))
                
            except Exception as e:
                print(f"Error building track '{track.get('name', 'UNKNOWN')}': {e}")
                
        # --- Mix all generated tracks ---
        if not generated_tracks:
            print("No tracks were generated. Exiting.")
            return
            
        print("\n--- Mixing Tracks ---")
        mixer = MultiTrackMixer(master_amplitude=master_amplitude)
        final_wave = mixer.mix_tracks(generated_tracks)
        
        # --- Save the final file ---
        final_wave_16bit = normalize_to_16bit(final_wave)
        save_wav(output_file, sample_rate, final_wave_16bit)