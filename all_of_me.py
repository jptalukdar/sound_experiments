# Import our custom tools
from sound_design import InstrumentFactory
from mixing import SongPlayer, MultiTrackMixer, save_wav, normalize_to_16bit
# Import the pre-filled aliases object
from composition_tools import aliases 

# --- Main Execution ---

if __name__ == "__main__":
    
    # 1. Setup global parameters
    SAMPLE_RATE = 44100
    TEMPO = 80  # Song tempo in BPM
    
    # 2. Instantiate our Instrument Factory
    factory = InstrumentFactory()
    print("-" * 30)

    # 3. Instantiate our instruments
    # We'll use two piano tracks
    piano_melody = factory.create_instrument(name='piano')
    piano_chords = factory.create_instrument(name='piano')
    print("-" * 30)

    # 4. --- Define Aliases ---
    # All notes (C4, E4, etc.) and chords (C_MAJOR, A_MINOR, etc.)
    # are already pre-loaded in the 'aliases' object.
    # We can just use them. 'REST' is also available as aliases.REST

    # 5. --- Define Song Parts (Notes & Rhythms) ---
    # The song is in 4/4 time. 1.0 = quarter note, 0.5 = 8th note, etc.

    # --- Verse Melody ("What would I do...") ---
    verse_melody_data = [
        # "What would I do without your smart mouth" (C Chord)
        (aliases.E4, 0.5), (aliases.E4, 0.5), (aliases.E4, 0.5), (aliases.E4, 0.5),
        (aliases.F4, 0.5), (aliases.E4, 0.5), (aliases.D4, 0.5), (aliases.C4, 0.5),
        # "Drawing me in, and you kicking me out" (Am Chord)
        (aliases.E4, 0.5), (aliases.E4, 0.5), (aliases.E4, 0.5), (aliases.E4, 0.5),
        (aliases.F4, 0.5), (aliases.E4, 0.5), (aliases.D4, 0.5), (aliases.C4, 0.5),
        # "Got my head spinning, no kidding..." (F Chord)
        (aliases.C4, 0.5), (aliases.C4, 0.5), (aliases.C4, 0.5), (aliases.D4, 0.5),
        (aliases.E4, 1.0), (aliases.D4, 1.0),
        # "I can't pin you down" (G Chord)
        (aliases.C4, 0.5), (aliases.C4, 0.5), (aliases.C4, 0.5), (aliases.D4, 0.5),
        (aliases.E4, 2.0)
    ]

    # --- Verse Chords (C, Am, F, G) ---
    verse_chord_data = [
        (aliases.C_MAJOR, 4.0),   # Bar 1
        (aliases.A_MINOR, 4.0),   # Bar 2
        (aliases.F_MAJOR, 4.0),   # Bar 3
        (aliases.G_MAJOR, 4.0),   # Bar 4
    ]
    
    # --- Chorus Melody ("'Cause all of me...") ---
    chorus_melody_data = [
        # "'Cause all... of me..." (Am Chord)
        (aliases.C5, 0.5), (aliases.C5, 0.5), (aliases.A4, 1.5), (aliases.REST, 0.5),
        # "...loves all... of you..." (F Chord)
        (aliases.A4, 0.5), (aliases.A4, 0.5), (aliases.G4, 1.5), (aliases.REST, 0.5),
        # "Love your curves and all your edges" (C Chord)
        (aliases.C4, 0.5), (aliases.D4, 0.5), (aliases.E4, 1.0), (aliases.C4, 0.5), (aliases.D4, 0.5), (aliases.E4, 1.0),
        # "All your perfect imperfections" (G Chord)
        (aliases.C4, 0.5), (aliases.D4, 0.5), (aliases.E4, 1.0), (aliases.F4, 1.0), (aliases.E4, 1.0),
    ]

    # --- Chorus Chords (Am, F, C, G) ---
    chorus_chord_data = [
        (aliases.A_MINOR, 4.0),   # Bar 1
        (aliases.F_MAJOR, 4.0),   # Bar 2
        (aliases.C_MAJOR, 4.0),   # Bar 3
        (aliases.G_MAJOR, 4.0),   # Bar 4
    ]

    # 6. --- Structure the Song ---
    # We'll play: Verse -> Verse -> Chorus -> Chorus
    
    melody_track_data = (verse_melody_data * 2) + (chorus_melody_data * 2)
    chord_track_data = (verse_chord_data * 2) + (chorus_chord_data * 2)

    # 7. --- Generate Waveforms (Create Players) ---
    
    print("\n--- Generating Tracks for 'All of Me' ---")
    
    # Generate Melody Track
    player_melody = SongPlayer(TEMPO, piano_melody, time_signature="4/4", sample_rate=SAMPLE_RATE)
    melody_wave = player_melody.generate_song_waveform(melody_track_data, amplitude=1.0)
    
    # Generate Chord Track
    player_chords = SongPlayer(TEMPO, piano_chords, time_signature="4/4", sample_rate=SAMPLE_RATE)
    chord_wave = player_chords.generate_song_waveform(chord_track_data, amplitude=1.0)
    
    print("-" * 30)

    # 8. --- Mix Tracks ---
    print("\n--- Mixing Tracks ---")
    track_mixer = MultiTrackMixer(master_amplitude=0.7)
    
    tracks_to_mix = [
        (melody_wave, 0.7),    # Melody is prominent
        (chord_wave, 0.5)      # Chords are softer, in the background
    ]
    
    final_song_wave = track_mixer.mix_tracks(tracks_to_mix)
    
    # 9. --- Save Final .wav File ---
    final_song_int = normalize_to_16bit(final_song_wave)
    save_wav("all_of_me_piano.wav", SAMPLE_RATE, final_song_int)
    
    print("\n--- All files generated. ---")