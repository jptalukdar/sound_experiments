Here is a context document summarizing the project's key details and architecture.

## 🎵 Project Overview

This is a modular, plugin-based audio synthesis engine. It allows a user to define instruments, compose multi-track songs using a simple note-based sequence, and mix all tracks into a final `.wav` file.

The project is built on **NumPy** for wave generation and **SciPy** for file output.

-----

## 📁 File Structure & Responsibilities

```
/
├── main.py
│   └── 🎵 The Composer: Defines song data, instruments, and mixing levels.
│
├── mixing.py
│   ├── 🎹 AudioMixer: (Internal) Generates a single note/chord wave.
│   ├──  sequencer SongPlayer: Turns a note sequence into a full track (NumPy array).
│   ├── 🎛️ MultiTrackMixer: Combines multiple tracks into a final song.
│   └── 💾 save_wav/normalize_to_16bit: I/O helper functions.
│
├── sound_design.py
│   └── 🏭 InstrumentFactory: The plugin loader. Scans the 'instruments'
│       folder and builds instruments by name (e.g., "piano").
│
├── music_tools.py
│   ├── 🎼 NoteFrequencies: Translates note names ("C4") to Hz (261.63).
│   └── 🎹 Chord: (Helper) Calculates frequencies for chords (not currently used by SongPlayer).
│
└── instruments/
    ├── __init__.py         (Makes the folder a Python package)
    ├── base_instrument.py  (🔌 The "Plugin Interface" - all instruments must inherit from this)
    ├── basic_synths.py     (Defines Sine, Square, Sawtooth)
    ├── piano.py            (Defines Piano)
    └── drums.py            (Defines Drums)
```

-----

## ⚙️ Core Workflow (Data Flow)

1.  **Run `main.py`**: This is the only file you run.
2.  **Plugin Loading**: `InstrumentFactory` is created. It automatically scans the `instruments/` directory and finds all classes that inherit from `BaseInstrument`.
3.  **Instrument Creation**: `main.py` asks the `InstrumentFactory` to create instances of the loaded instruments by name (e.g., `piano = factory.create_instrument('piano')`).
4.  **Song Definition**: `main.py` defines song data as lists of tuples: `[ (['C4', 'E4'], 2), ... ]` (a list of notes and a duration in beats).
5.  **Track Generation**:
      * A `SongPlayer` is created for *each track* (e.g., `player_piano`, `player_drums`).
      * Each `SongPlayer` is given its specific instrument and tempo.
      * `player.generate_song_waveform(song_data)` is called.
      * `SongPlayer` loops through the `song_data` and uses its instrument's `.get_waveform()` method to generate each note.
      * It concatenates all note waveforms into one long NumPy array (a "track").
6.  **Mixing**:
      * `main.py` creates a `MultiTrackMixer`.
      * It passes all the generated tracks and their desired volumes to `mixer.mix_tracks()`. Example: `[ (melody_wave, 0.7), (drum_wave, 0.4) ]`.
      * The mixer combines all arrays, normalizes them, and applies a master volume.
7.  **Saving**:
      * The final NumPy array from the mixer is passed to `normalize_to_16bit()`.
      * The resulting 16-bit integer array is passed to `save_wav()` to create the final `.wav` file.

-----

## 🔌 How to Add a New Instrument

1.  Create a new file in the `instruments/` directory (e.g., `flute.py`).
2.  Inside, import the base class: `from .base_instrument import BaseInstrument`.
3.  Create your class: `class Flute(BaseInstrument):`.
4.  Implement the **required** method: `_generate_wave(self, t, frequencies, sample_rate)`. This is where you put your wave generation logic (e.g., `np.sin(...)`).
5.  (Optional) Define a custom `__init__` to set default ADSR (Attack, Decay, Sustain) values.
6.  The `InstrumentFactory` will now find it automatically.
7.  Use it in `main.py`: `flute_sound = factory.create_instrument('flute')`.