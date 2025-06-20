import cv2
import mediapipe as mp
import serial
import time

# === Arduino Setup ===
arduino = serial.Serial(port='COM15', baudrate=9600, timeout=1)
time.sleep(2)

# Relay states [Thumb, Index, Middle, Ring, Pinky]
relay_state = [1, 1, 1, 1, 1]
arduino.write(bytes(relay_state))  # Initialize: all OFF

# Previous finger states
prev_finger_up = [0, 0, 0, 0, 0]

# === Mediapipe Setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# === Finger Detection and Toggling ===
def detect_fingers(hand_landmarks):
    global relay_state, prev_finger_up

    finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
    thumb_tip = 4
    current_up = [0, 0, 0, 0, 0]  # [Thumb, Index, Middle, Ring, Pinky]

    # Thumb detection (X-axis)
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
        current_up[0] = 1

    # Other fingers detection (Y-axis)
    for idx, tip in enumerate(finger_tips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            current_up[idx + 1] = 1

    # Toggle logic for Thumb, Index, Middle, Ring only
    for i in [0, 1, 2, 3]:  # Skip Pinky (i=4)
        if prev_finger_up[i] == 1 and current_up[i] == 0:
            relay_state[i] ^= 1
            print(f"🔁 Finger {i} toggled Relay {i+1} to {relay_state[i]}")

    # Always disable pinky (index 4)
    relay_state[4] = 0

    # Update previous state
    prev_finger_up[:] = current_up
    return relay_state

# === Main Loop ===
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers_state = detect_fingers(hand_landmarks)
            arduino.write(bytes(fingers_state))
            print("📤 Sent to Arduino:", fingers_state)

    cv2.imshow('Hand Tracking', image)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
