# Import our custom tools
from sound_design import InstrumentFactory
from mixing import SongPlayer, MultiTrackMixer, save_wav, normalize_to_16bit
# Import the pre-filled aliases object
from composition_tools import aliases as note

# --- Main Execution ---

if __name__ == "__main__":
    
    # 1. Setup global parameters
    SAMPLE_RATE = 44100
    TEMPO = 120  # The actual song is ~123 BPM
    
    # 2. Instantiate our Instrument Factory
    factory = InstrumentFactory()
    print("-" * 30)

    # 3. Instantiate our instruments
    bass_synth = factory.create_instrument(name='bass')
    vocal_piano = factory.create_instrument('piano')
    drum_kit = factory.create_instrument('drums')
    print("-" * 30)

    # 4. --- Define Aliases ---
    # Notes and Chords (C2-B5) are now pre-loaded from 'aliases'.
    # We just need to add our project-specific drum note.
    
    note.add_chords(
        KICK = ['C4'],
        SNARE = ['D4'],
        HAT = ['G4'],
        KICK_HAT = ['C4', 'G4'],
        SNARE_HAT = ['D4', 'G4']
    )
    # R is automatically added as note.REST

    # 5. --- Define Song Parts (Notes & Rhythms) ---
    # The song data now uses the aliases object.

    # The main 4-bar riff
    bass_riff_verse = [
        (note.E3, 1.5), (note.E3, 0.5), (note.G3, 1.0), (note.E3, 1.0),  # Bar 1
        (note.D3, 1.5), (note.D3, 0.5), (note.C3, 2.0),            # Bar 2
        (note.B2, 4.0),                                  # Bar 3
        (note.REST,  4.0),                               # Bar 4
    ]

    # "I'm gon-na fight 'em off..."
    verse_melody_a = [
        (note.E4, 1.5), (note.E4, 0.5), (note.G4, 1.0), (note.E4, 1.0),  # Bar 1
        (note.D4, 1.5), (note.D4, 0.5), (note.C4, 2.0),            # Bar 2
        (note.B3, 4.0),                                  # Bar 3
        (note.REST, 4.0),                                # Bar 4
    ]
    # "...A sev-en na-tion ar-my..."
    verse_melody_b = [
        (note.E4, 1.5), (note.E4, 0.5), (note.G4, 1.0), (note.E4, 1.0),  # Bar 5
        (note.D4, 1.5), (note.D4, 0.5), (note.C4, 2.0),            # Bar 6
        (note.B3, 4.0),                                  # Bar 7
        (note.REST, 4.0),                                # Bar 8
    ]
    
    # Simple 1-bar "four on the floor" beat (with 8th notes)
    drum_beat = [
        (note.KICK_HAT, 0.5), (note.HAT, 0.5),  # 1
        (note.SNARE_HAT, 0.5), (note.HAT, 0.5), # 2
        (note.KICK_HAT, 0.5), (note.HAT, 0.5),  # 3
        (note.SNARE_HAT, 0.5), (note.HAT, 0.5), # 4
    ]

    # 6. --- Structure the Song ---
    
    # Repeat the 4-bar riff 4 times (16 bars total)
    bass_track_data = bass_riff_verse * 4
    
    # Repeat the 1-bar drum beat 16 times
    drum_track_data = drum_beat * 16
    
    # Create the full melody track (8 bars of melody, 8 bars of rest)
    melody_track_data = verse_melody_a + verse_melody_b + [ (note.REST, 16.0) ]

    # 7. --- Generate Waveforms (Create Players) ---
    
    print("\n--- Generating Tracks ---")
    
    # Generate Bass Track
    player_bass = SongPlayer(TEMPO, bass_synth, time_signature="4/4", sample_rate=SAMPLE_RATE)
    bass_wave = player_bass.generate_song_waveform(bass_track_data, amplitude=1.0)
    
    # Generate Drum Track
    player_drums = SongPlayer(TEMPO, drum_kit, time_signature="4/4", sample_rate=SAMPLE_RATE)
    drum_wave = player_drums.generate_song_waveform(drum_track_data, amplitude=1.0)
    
    # Generate Melody Track
    player_piano = SongPlayer(TEMPO, vocal_piano, time_signature="4/4", sample_rate=SAMPLE_RATE)
    melody_wave = player_piano.generate_song_waveform(melody_track_data, amplitude=1.0)
    
    print("-" * 30)

    # 8. --- Mix Tracks ---
    print("\n--- Mixing Tracks ---")
    track_mixer = MultiTrackMixer(master_amplitude=0.7)
    
    tracks_to_mix = [
        (bass_wave, 0.8),    # Bass is loud and central
        (drum_wave, 0.3),    # Drums are solid
        (melody_wave, 0.8)   # Melody is slightly softer
    ]
    
    final_song_wave = track_mixer.mix_tracks(tracks_to_mix)
    
    # 9. --- Save Final .wav File ---
    final_song_int = normalize_to_16bit(final_song_wave)
    save_wav("seven_nation_army_with_bass.wav", SAMPLE_RATE, final_song_int)
    
    print("\n--- All files generated. ---")