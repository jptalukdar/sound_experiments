import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd

# --- Import from your existing synth framework ---
# We assume these files are in the same directory
try:
    from sound_design import InstrumentFactory
    from music_tools import NoteFrequencies
except ImportError:
    print("Error: Could not import your synthesizer files.")
    print("Make sure 'live_piano.py' is in the same directory as 'sound_design.py' and 'music_tools.py'")
    exit()

# --- 1. Global Setup ---

# Audio Settings
SAMPLE_RATE = 44100
NOTE_DURATION_S = 0.3  # How long each note plays
MASTER_AMPLITUDE = 0.7

# Note Mapping (C-Major Scale)
# We will divide the screen into this many "keys"
NOTES_TO_PLAY = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
NUM_KEYS = len(NOTES_TO_PLAY)

# --- 2. Initialize Synthesizer ---
print("Loading synthesizer...")
try:
    factory = InstrumentFactory()
    # We use the 'piano' instrument, as requested
    piano = factory.create_instrument('piano') 
    freq_calc = NoteFrequencies()
    print("Synthesizer loaded.")
except Exception as e:
    print(f"Error loading synthesizer: {e}")
    print("Make sure your 'piano' instrument plugin exists in the 'instruments/' folder.")
    exit()

# --- 3. Initialize Video and Hand Tracking ---
print("Starting video capture...")
cap = cv2.VideoCapture(0)  # 0 is the default webcam
if not cap.isOpened():
    print("Error: Cannot open webcam.")
    exit()

# MediaPipe Hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,              # Track only one hand
    min_detection_confidence=0.7, # Higher confidence
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# --- 4. Main Loop ---

# State variables
last_key_index = -1  # -1 means no key is pressed
current_key_index = -1

print("Starting live piano. Press 'q' to quit.")

while True:
    # --- A. Get Video Frame ---
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the frame horizontally (for a mirror-like view)
    frame = cv2.flip(frame, 1)
    
    # Get frame dimensions
    h, w, _ = frame.shape
    
    # Create a semi-transparent overlay to draw keys on
    overlay = frame.copy()

    # --- B. Process Hand ---
    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    current_key_index = -1  # Reset on each frame

    if results.multi_hand_landmarks:
        # Get the first (and only) hand
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # --- C. Get Finger Position & Map to Key ---
        # Get the landmark for the tip of the index finger (Landmark 8)
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        # Convert normalized (0.0 - 1.0) coordinates to pixel coordinates
        cx = int(index_tip.x * w)
        cy = int(index_tip.y * h)

        # Map the X-coordinate to one of our "keys"
        key_width = w / NUM_KEYS
        current_key_index = int(cx / key_width)
        
        # Draw all landmarks on the original frame
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Draw a circle at the finger tip
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    # --- D. Play Audio ---
    if current_key_index != last_key_index:
        # State has changed!
        sd.stop()  # Stop any note that was playing
        
        if current_key_index != -1:
            # A new key is pressed
            try:
                note_name = NOTES_TO_PLAY[current_key_index]
                print(f"Key: {current_key_index}  Note: {note_name}")

                # Get the frequency for the note
                freq = freq_calc.get_frequency(note_name)
                
                if freq:
                    # Use your instrument to get the waveform
                    waveform = piano.get_waveform(
                        frequencies=[freq],
                        duration_s=NOTE_DURATION_S,
                        sample_rate=SAMPLE_RATE,
                        amplitude=MASTER_AMPLITUDE
                    )
                    
                    # Play the waveform
                    sd.play(waveform, SAMPLE_RATE)

            except Exception as e:
                print(f"Error playing sound: {e}")
                
        last_key_index = current_key_index # Update the state

    # --- E. Visualize the "Piano" ---
    key_width = w // NUM_KEYS
    for i in range(NUM_KEYS):
        x1 = i * key_width
        x2 = (i + 1) * key_width
        
        # Highlight the active key
        if i == current_key_index:
            cv2.rectangle(overlay, (x1, 0), (x2, h), (0, 255, 0), -1) # Solid green

        # Draw the key divider
        cv2.rectangle(frame, (x1, 0), (x2, h), (255, 255, 255), 1)
        
        # Draw the note name
        cv2.putText(frame, NOTES_TO_PLAY[i], (x1 + 10, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Blend the overlay with the frame
    frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
    
    # Re-draw text on top of the blended image
    for i in range(NUM_KEYS):
        x1 = i * key_width
        cv2.putText(frame, NOTES_TO_PLAY[i], (x1 + 10, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # --- F. Display and Exit ---
    cv2.imshow("Live Piano - (Press 'q' to quit)", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# --- 5. Cleanup ---
print("Shutting down...")
cap.release()
cv2.destroyAllWindows()
sd.stop()