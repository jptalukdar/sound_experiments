# Import our custom tools
from sound_design import InstrumentFactory
from mixing import SongPlayer, MultiTrackMixer, save_wav, normalize_to_16bit

# --- Main Execution (Example Usage) ---

if __name__ == "__main__":
    
    # 1. Setup global parameters
    SAMPLE_RATE = 44100
    
    # --- Aliases for Notes ---
    C4 = ['C4']; D4 = ['D4']; E4 = ['E4']; F4 = ['F4']; G4 = ['G4']; A4 = ['A4']
    B4 = ['B4']; C5 = ['C5']; D5 = ['D5']; E5 = ['E5']
    REST = []
    
    # --- Aliases for Chords ---
    C_MAJOR = ['C4', 'E4', 'G4']
    G_MAJOR = ['G4', 'B4', 'D5']
    A_MINOR = ['A4', 'C5', 'E5']
    F_MAJOR = ['F4', 'A4', 'C5']
    
    # --- Aliases for Drums ---
    KICK = ['C4']; SNARE = ['D4']; TOM = ['F4']; HAT = ['G4']
    
    # 2. Instantiate our Instrument Factory
    factory = InstrumentFactory()
    print("-" * 30)

    # 3. Instantiate our instruments by name
    piano_sound = factory.create_instrument('piano')
    synth_sound = factory.create_instrument('sawtooth', attack_s=0.05, decay_s=0.1, sustain_level=0.7)
    drum_kit = factory.create_instrument('drums')
    print("-" * 30)
    
    # --- 4. EXAMPLE 1: 4/4 Time ---
    
    # A simple drum beat (4/4)
    # num_beats = 0.5 means an 8th note
    drum_beat_4_4 = [
        (KICK, 0.5), (HAT, 0.5), (SNARE, 0.5), (HAT, 0.5),
        (KICK, 0.5), (HAT, 0.5), (SNARE, 0.5), (HAT, 0.5),
    ] * 8
    
    # A simple chord progression (4/4)
    # num_beats = 4.0 means a whole note
    chord_progression_4_4 = [
        (C_MAJOR, 4), (G_MAJOR, 4),
    ] * 2

    # --- Generate 4/4 Tracks ---
    print("\n--- Generating 4/4 Tracks ---")
    player_drums = SongPlayer(tempo=120, instrument=drum_kit, time_signature="4/4", sample_rate=SAMPLE_RATE)
    drum_wave = player_drums.generate_song_waveform(drum_beat_4_4, amplitude=1.0)
    
    player_synth = SongPlayer(tempo=120, instrument=synth_sound, time_signature="4/4", sample_rate=SAMPLE_RATE)
    chord_wave = player_synth.generate_song_waveform(chord_progression_4_4, amplitude=1.0)
    
    # --- Mix 4/4 Tracks ---
    track_mixer = MultiTrackMixer(master_amplitude=0.7)
    final_4_4_mix = track_mixer.mix_tracks([
        (drum_wave, 0.8),
        (chord_wave, 0.4)
    ])
    save_wav("song_4_4_mix.wav", SAMPLE_RATE, normalize_to_16bit(final_4_4_mix))
    print("-" * 30)

    # --- 5. EXAMPLE 2: 6/8 Time ---
    
    # A simple jig melody (6/8)
    # num_beats = 0.5 means an 8th note
    # num_beats = 1.5 means a dotted quarter note
    jig_melody_6_8 = [
        (D4, 0.5), (E4, 0.5), (F4, 0.5), (D4, 0.5), (E4, 0.5), (F4, 0.5), # Bar 1
        (G4, 0.5), (A4, 0.5), (B4, 0.5), (G4, 1.5),              # Bar 2
        (D4, 0.5), (E4, 0.5), (F4, 0.5), (D4, 0.5), (E4, 0.5), (F4, 0.5), # Bar 3
        (E4, 1.5), (D4, 1.5),                                    # Bar 4
    ] * 4
    
    # A simple drum beat (6/8)
    # KICK on 1, SNARE on 4
    drum_beat_6_8 = [
        (KICK, 0.5), (HAT, 0.5), (HAT, 0.5),
        (SNARE, 0.5), (HAT, 0.5), (HAT, 0.5),
    ] * 16

    # --- Generate 6/8 Tracks ---
    print("\n--- Generating 6/8 Tracks ---")
    # Note: 180 BPM in 6/8 time (180 8th-notes per minute)
    player_piano = SongPlayer(tempo=180, instrument=piano_sound, time_signature="6/8", sample_rate=SAMPLE_RATE)
    jig_wave = player_piano.generate_song_waveform(jig_melody_6_8, amplitude=1.0)
    
    player_drums.tempo = 180
    player_drums.time_signature = "6/8"
    player_drums.beat_unit = 8
    player_drums.base_beat_duration_s = 60.0 / 180
    player_drums.quarter_note_duration_s = player_drums.base_beat_duration_s * (8.0 / 4.0)
    
    drum_wave_6_8 = player_drums.generate_song_waveform(drum_beat_6_8, amplitude=1.0)

    # --- Mix 6/8 Tracks ---
    track_mixer_6_8 = MultiTrackMixer(master_amplitude=0.7)
    final_6_8_mix = track_mixer_6_8.mix_tracks([
        (jig_wave, 0.7),
        (drum_wave_6_8, 0.5)
    ])
    save_wav("song_6_8_jig.wav", SAMPLE_RATE, normalize_to_16bit(final_6_8_mix))
    print("-" * 30)

    print("\n--- All files generated. ---")