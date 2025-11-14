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
    
    # --- Aliases for Melody ---
    C4 = ['C4']
    D4 = ['D4']
    E4 = ['E4']
    F4 = ['F4']
    G4 = ['G4']
    A4 = ['A4']
    REST = []
    
    # The melody data
    twinkle_twinkle_melody = [
        (C4, 1), (C4, 1), (G4, 1), (G4, 1),
        (A4, 1), (A4, 1), (G4, 2),
        (F4, 1), (F4, 1), (E4, 1), (E4, 1),
        (D4, 1), (D4, 1), (C4, 2),
        (G4, 1), (G4, 1), (F4, 1), (F4, 1),
        (E4, 1), (E4, 1), (D4, 2),
    ] * 2 # Play it twice
    
    # --- Aliases for Chords ---
    C_MAJOR = ['C4', 'E4', 'G4']
    G_MAJOR = ['G4', 'B4', 'D5']
    A_MINOR = ['A4', 'C5', 'E5']
    F_MAJOR = ['F4', 'A4', 'C5']
    
    # A simple chord progression (C-G-Am-F), repeated
    chord_progression = [
        (C_MAJOR, 4), (G_MAJOR, 4), (A_MINOR, 4), (F_MAJOR, 4),
    ] * 4 # Repeat to match melody length

    # --- Aliases for Drums ---
    # We map them to the notes defined in instruments/drums.py
    KICK = ['C4']
    SNARE = ['D4']
    TOM = ['F4']
    HAT = ['G4']
    KICK_SNARE = ['C4', 'D4'] # Play two at once

    # A simple drum beat (four-on-the-floor)
    drum_beat = [
        (KICK, 0.5), (HAT, 0.5), (HAT, 0.5), (HAT, 0.5),
        (SNARE, 0.5), (HAT, 0.5), (HAT, 0.5), (HAT, 0.5),
        (KICK, 0.5), (HAT, 0.5), (HAT, 0.5), (HAT, 0.5),
        (SNARE, 0.5), (TOM, 0.5), (HAT, 0.5), (HAT, 0.5),
    ] * 16 # Repeat to match song length

    # 3. Instantiate our Instrument Factory
    # This will automatically find and load 'drums'
    factory = InstrumentFactory()

    # 4. Instantiate our instruments by name
    piano_sound = factory.create_instrument('piano')
    
    synth_sound = factory.create_instrument(
        name='sawtooth',
        attack_s=0.05,
        decay_s=0.3,
        sustain_level=0.7
    )
    
    # Create the new drums instrument
    drum_kit = factory.create_instrument('drums')

    # 5. --- Generate Melody Track (Piano) ---
    print("\n--- Generating Melody (Piano) ---")
    player_piano = SongPlayer(tempo=TEMPO, instrument=piano_sound, sample_rate=SAMPLE_RATE)
    melody_wave = player_piano.generate_song_waveform(twinkle_twinkle_melody, amplitude=1.0)
    save_wav("song_melody_piano.wav", SAMPLE_RATE, normalize_to_16bit(melody_wave))


    # 6. --- Generate Chords Track (Synth) ---
    print("\n--- Generating Chords (Sawtooth Synth) ---")
    player_synth = SongPlayer(tempo=TEMPO, instrument=synth_sound, sample_rate=SAMPLE_RATE)
    # Slower tempo for the chords
    player_synth.tempo = 70 
    player_synth.beat_duration_s = 60.0 / player_synth.tempo
    chord_wave = player_synth.generate_song_waveform(chord_progression, amplitude=1.0)
    save_wav("song_chords_synth.wav", SAMPLE_RATE, normalize_to_16bit(chord_wave))

    # 7. --- Generate Drum Track ---
    print("\n--- Generating Drums ---")
    player_drums = SongPlayer(tempo=TEMPO, instrument=drum_kit, sample_rate=SAMPLE_RATE)
    drum_wave = player_drums.generate_song_waveform(drum_beat, amplitude=1.0)
    save_wav("song_drums.wav", SAMPLE_RATE, normalize_to_16bit(drum_wave))
    

    # 8. --- Mix all tracks together ---
    print("\n--- Mixing Tracks ---")
    track_mixer = MultiTrackMixer(master_amplitude=0.7)
    
    tracks_to_mix = [
        (melody_wave, 0.6),  # Piano melody
        (chord_wave, 0.3),   # Synth chords
        (drum_wave, 0.8)     # Drums
    ]
    
    final_song_wave = track_mixer.mix_tracks(tracks_to_mix)
    
    # 9. Normalize and save the final song
    final_song_int = normalize_to_16bit(final_song_wave)
    save_wav("song_final_mix.wav", SAMPLE_RATE, final_song_int)
    
    print("\n--- All files generated. ---")