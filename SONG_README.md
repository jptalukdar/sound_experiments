# How to Write a .song File

This guide explains the simple text-based format for composing music with the Python Music Synthesizer.

Overview

The .song format is read from top to bottom. It's built from 5 simple concepts:

Global Settings: Define the master tempo, output file, etc.

Tracks: Define a new musical part (e.g., [TRACK: drums]).

Track Settings: Define the instrument, volume, etc., for that track.

Note Data: The actual notes to be played.

Commands: Special actions like [REPEAT: n].

Lines starting with # are comments and will be ignored.

1. Global Settings

These settings must be placed at the top of the file, before any [TRACK] definitions. They are key-value pairs.

# --- Global Settings ---
TEMPO: 120
SAMPLE_RATE: 44100
MASTER_AMPLITUDE: 0.7
OUTPUT_FILE: my_song.wav


TEMPO: The speed of the song in Beats Per Minute (BPM).

SAMPLE_RATE: The audio quality (44100 is standard).

MASTER_AMPLITUDE: The final "master volume" for the whole song (0.0 to 1.0).

OUTPUT_FILE: The name of the .wav file to create (it will be saved in the sounds/ directory).

2. Defining a Track

To start a new instrument or musical part, use the [TRACK: name] tag. The name is for your own reference (e.g., "bass", "melody", "drums").

# --- Track 1: Bassline ---
[TRACK: bass]
... (settings and notes go here) ...

# --- Track 2: Drums ---
[TRACK: drums]
... (settings and notes go here) ...


3. Track Settings

Immediately after a [TRACK] tag, you must specify its settings.

[TRACK: lead_synth]
INSTRUMENT: sawtooth
VOLUME: 0.6
TIME_SIGNATURE: 4/4


INSTRUMENT: (Required) The name of the instrument plugin to use (e.g., piano, bass, drums, sine, sawtooth). Must match a loaded plugin.

VOLUME: (Required) The volume for this specific track (0.0 to 1.0).

TIME_SIGNATURE: (Optional) The time signature for this track. Defaults to 4/4 if not provided.

4. Writing Note Data

This is the main part of your song. Each line represents a "note event".

The format is: [ALIAS_1] [ALIAS_2] ... [DURATION]

Alias: The name of the note or chord. All aliases are case-insensitive.

Notes: C4, Fsharp3, B2

Chords: C_MAJOR, A_MINOR, G_DIM

Drums: KICK, SNARE, HAT

Rest: REST

Duration: (Required) The last item on the line is always the duration in quarter notes.

1.0 = Quarter Note

0.5 = 8th Note

2.0 = Half Note

4.0 = Whole Note

1.5 = Dotted Quarter Note

Examples:

# A single C4 note for 1 quarter note
C4 1.0

# A C-Major chord for 1.5 beats (dotted quarter)
C_MAJOR 1.5

# A kick and hi-hat played together for an 8th note
KICK HAT 0.5

# A rest for 2 beats (half note)
REST 2.0


5. Commands

Commands are special actions that apply to the track they are in.

[REPEAT: n]

This command repeats all the note data above it in the current track n additional times.

[TRACK: drums]
INSTRUMENT: drums
VOLUME: 0.5

# This is a 1-bar beat
KICK 1.0
SNARE 1.0
KICK 1.0
SNARE 1.0

# This will play the 1-bar beat 3 more times
# for a total of 4 bars.
[REPEAT: 3]
