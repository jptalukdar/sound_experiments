import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd
import threading

# --- 1. Global Audio Settings ---
SAMPLE_RATE = 44100
MIN_FREQ = 220  # A3
MAX_FREQ = 880  # A5
MAX_HANDS = 2   # Max number of hands to track and mix
MAX_AMP_PER_HAND = 0.4 # Max amplitude for one hand (to prevent clipping)
DETUNE_HZ = 5   # --- NEW: How much to detune the right channel for binaural effect ---

# --- 2. Shared State (for communication between threads) ---
data_lock = threading.Lock()
# We now have a list of oscillators, one for each potential hand
g_oscillators = [
    {'freq': MIN_FREQ, 'amp': 0.0, 'phase': 0.0} for _ in range(MAX_HANDS)
]

# --- 3. Audio Callback Function ---
# This function is called by the sounddevice library in a separate thread
# whenever it needs more audio samples.
def audio_callback(outdata, frames, time, status):
    """Fills the output buffer (outdata) with audio samples."""
    global g_oscillators, data_lock
    
    # --- MODIFIED: Create a 2-channel (stereo) buffer ---
    final_wave = np.zeros((frames, 2))
    
    # Get a thread-safe copy of the oscillator states
    # We do this to minimize how long we hold the lock
    current_oscillators = []
    with data_lock:
        for osc in g_oscillators:
            current_oscillators.append(osc.copy())

    # Generate wave for each oscillator and mix
    for i in range(MAX_HANDS):
        freq = current_oscillators[i]['freq']
        amp = current_oscillators[i]['amp']
        phase = current_oscillators[i]['phase']

        if amp > 0.001: # Only process if the hand is active
            # Create an array of time points for this buffer
            t = (phase + np.arange(frames)) / SAMPLE_RATE
            
            # --- MODIFIED: Generate Left and Right channels ---
            
            # 1. Left Channel (Main Frequency)
            wave_left = amp * (2 * (t * freq - np.floor(0.5 + t * freq)))
            
            # 2. Right Channel (Detuned Frequency)
            freq_right = freq + DETUNE_HZ
            wave_right = amp * (2 * (t * freq_right - np.floor(0.5 + t * freq_right)))
            
            # Add it to the final mix (L/R)
            final_wave[:, 0] += wave_left
            final_wave[:, 1] += wave_right
            # --- END MODIFICATION ---
            
            # Update the global phase for this oscillator
            # This is critical for continuous, click-free sound
            new_phase = (phase + frames) % SAMPLE_RATE
            with data_lock:
                g_oscillators[i]['phase'] = new_phase
        else:
            # If amplitude is 0, reset phase
            with data_lock:
                 g_oscillators[i]['phase'] = 0.0

    # --- MODIFIED: Reshape for 2-channel output ---
    outdata[:] = final_wave


# --- 4. Main Program (Video Tracking) ---
def main():
    global g_oscillators, data_lock

    # --- Initialize Video and Hand Tracking ---
    print("Starting video capture...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam.")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=MAX_HANDS, # Update to track multiple hands
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils

    # --- Initialize and Start Audio Stream ---
    try:
        stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            # --- MODIFIED: Set channels to 2 for stereo ---
            channels=2,
            callback=audio_callback
        )
        stream.start()
    except Exception as e:
        print(f"Error starting audio stream: {e}")
        cap.release()
        return

    print("Starting Theremin. Press 'q' to quit.")

    while True:
        # --- Get Video Frame ---
        success, frame = cap.read()
        if not success:
            continue
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # --- Process Hands ---
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # A list to hold states for hands found in this frame
        current_hand_states = [] 

        if results.multi_hand_landmarks:
            # Loop through all detected hands
            for hand_landmarks in results.multi_hand_landmarks:
                
                # Get index finger tip (Landmark 8)
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                # Get normalized coordinates (0.0 to 1.0)
                norm_x = index_tip.x
                norm_y = index_tip.y
                
                # --- Map Position to Audio Parameters ---
                # X-axis (Left/Right) controls Frequency
                log_min = np.log(MIN_FREQ)
                log_max = np.log(MAX_FREQ)
                log_freq = log_min + (log_max - log_min) * norm_x
                
                # Round to the nearest integer frequency
                current_freq = round(np.exp(log_freq))

                # Y-axis (Up/Down) controls Amplitude
                current_amp = (1.0 - norm_y) * MAX_AMP_PER_HAND
                current_amp = max(0.0, current_amp) # Ensure it's not negative
                
                # Add this hand's state to our list
                current_hand_states.append({'freq': current_freq, 'amp': current_amp})
                
                # --- Draw on frame ---
                finger_x = int(norm_x * w)
                finger_y = int(norm_y * h)
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                cv2.circle(frame, (finger_x, finger_y), 10, (0, 255, 0), cv2.FILLED)

        # --- Update Shared Audio State ---
        with data_lock:
            for i in range(MAX_HANDS):
                if i < len(current_hand_states):
                    # A hand is active, update its oscillator
                    g_oscillators[i]['freq'] = current_hand_states[i]['freq']
                    g_oscillators[i]['amp'] = current_hand_states[i]['amp']
                else:
                    # No hand for this oscillator, set amplitude to 0
                    g_oscillators[i]['amp'] = 0.0

        # --- Display Info on Frame ---
        # We read back from the global state for a consistent display
        with data_lock:
            osc_display_list = [osc.copy() for osc in g_oscillators]

        for i, osc in enumerate(osc_display_list):
            if osc['amp'] > 0.01: # Only show active hands
                # Display the frequency. Since it's rounded, .00 will be shown.
                text = f"Hand {i}: {osc['freq']:.2f} Hz, {osc['amp']:.2f} Vol"
                cv2.putText(frame, text, (10, h - 10 - (i * 30)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # --- Display and Exit ---
        cv2.imshow("Live Theremin - (Press 'q' to quit)", frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    # --- Cleanup ---
    print("Shutting down...")
    stream.stop()
    stream.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()