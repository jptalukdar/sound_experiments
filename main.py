# Import our custom tools
from sound_design import InstrumentFactory
from mixing import SongPlayer, MultiTrackMixer, save_wav, normalize_to_16bit

# --- Main Execution (Example Usage) ---

if __name__ == "__main__":
    
    # 1. Setup global parameters
    SAMPLE_RATE = 44100
    TEMPO = 140 # Beats Per Minute

    # 2. Define our song (Twinkle, Twinkle, Little Star)
    # The format is: [ ( [list_of_notes], num_beats ), ... ]
    # An empty list [] means a rest.
    
    # Define note "aliases" for convenience
    C4 = ['C4']
    D4 = ['D4']
    E4 = ['E4']
    F4 = ['F4']
    G4 = ['G4']
    A4 = ['A4']
    REST = []
    
    # Define a C Major chord
    C_MAJOR_CHORD = ['C4', 'E4', 'G4']

    # The song data
    twinkle_twinkle_melody = [
        (C4, 1), (C4, 1), (G4, 1), (G4, 1),
        (A4, 1), (A4, 1), (G4, 2),
        (F4, 1), (F4, 1), (E4, 1), (E4, 1),
        (D4, 1), (D4, 1), (C4, 2),
        (G4, 1), (G4, 1), (F4, 1), (F4, 1),
        (E4, 1), (E4, 1), (D4, 2),
        (G4, 1), (G4, 1), (F4, 1), (F4, 1),
        (E4, 1), (E4, 1), (D4, 2),
        (C4, 1), (C4, 1), (G4, 1), (G4, 1),
        (A4, 1), (A4, 1), (G4, 2),
        (F4, 1), (F4, 1), (E4, 1), (E4, 1),
        (D4, 1), (D4, 1), (C4, 2),
    ]
    
    # A simple chord progression (C-G-Am-F)
    chord_progression = [
        (['C4', 'E4', 'G4'], 4), # C Major
        (['G4', 'B4', 'D5'], 4), # G Major
        (['A4', 'C5', 'E5'], 4), # A Minor
        (['F4', 'A4', 'C5'], 4), # F Major
    ]

    # 3. Instantiate our Instrument Factory
    # This will automatically find and load plugins from the 'instruments/' dir
    factory = InstrumentFactory()

    # 4. Instantiate our instruments by name
    # The 'piano' plugin defines its own default envelope
    piano_sound = factory.create_instrument('piano')
    
    # We can override defaults for any instrument
    synth_sound = factory.create_instrument(
        name='sawtooth',
        attack_s=0.05,
        decay_s=0.1,
        sustain_level=0.7
    )
    
    # 5. Instantiate our player with the piano sound
    player = SongPlayer(tempo=TEMPO, instrument=piano_sound, sample_rate=SAMPLE_RATE)
    
    # 6. Generate the "Twinkle Twinkle" melody
    print("\n--- Generating Melody (Piano) ---")
    # Generate at full amplitude; we will set volume in the mixer
    melody_wave = player.generate_song_waveform(twinkle_twinkle_melody, amplitude=1.0)
    
    # 7. Normalize and save (optional, good for debugging)
    melody_wave_int = normalize_to_16bit(melody_wave)
    save_wav("song_melody_piano.wav", SAMPLE_RATE, melody_wave_int)

    # 8. Generate the chord progression with the synth sound
    print("\n--- Generating Chords (Sawtooth Synth) ---")
    
    # Change the player's instrument and tempo
    player.instrument = synth_sound
    player.tempo = 80 # Slow down the tempo for the chords
    player.beat_duration_s = 60.0 / player.tempo # Update beat duration
    
    # Generate at full amplitude; we will set volume in the mixer
    chord_wave = player.generate_song_waveform(chord_progression, amplitude=1.0)
    
    # 9. Normalize and save (optional, good for debugging)
    chord_wave_int = normalize_to_16bit(chord_wave)
    save_wav("song_chords_synth.wav", SAMPLE_RATE, chord_wave_int)
    
    # 10. --- Mix the two tracks together ---
    print("\n--- Mixing Tracks ---")
    track_mixer = MultiTrackMixer(master_amplitude=0.8)
    
    # Create a list of (track, volume) tuples
    tracks_to_mix = [
        (melody_wave, 0.7),  # Piano melody at 70% volume
        (chord_wave, 0.4)   # Synth chords at 40% volume
    ]
    
    # Mix the tracks using the new method
    final_song_wave = track_mixer.mix_tracks(tracks_to_mix)
    
    # 11. Normalize and save the final song
    final_song_int = normalize_to_16bit(final_song_wave)
    save_wav("song_final_mix.wav", SAMPLE_RATE, final_song_int)
    
    print("\n--- All files generated. ---")