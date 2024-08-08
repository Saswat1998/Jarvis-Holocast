import cv2
import mediapipe as mp
import json
import os
import time
# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Initialize Webcam
cap = cv2.VideoCapture(0)

initial_distance = None
zoom_factor = 1.0
pinching = False

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    gesture_data = {}

    if results.multi_hand_landmarks:
        if len(results.multi_hand_landmarks) == 1:
            hand = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

            # Get coordinates of the index finger tip and thumb tip
            index_finger_tip = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convert coordinates to pixel values
            index_x = int(index_finger_tip.x * img.shape[1])
            index_y = int(index_finger_tip.y * img.shape[0])
            thumb_x = int(thumb_tip.x * img.shape[1])
            thumb_y = int(thumb_tip.y * img.shape[0])

            # Detect pinch gesture (if the distance between index finger tip and thumb tip is small)
            if abs(index_x - thumb_x) < 40 and abs(index_y - thumb_y) < 40:
                gesture_data = {"gesture": "pinch_move", "x": index_x, "y": index_y}
                pinching = False

        elif len(results.multi_hand_landmarks) == 2:
            hand1 = results.multi_hand_landmarks[0]
            hand2 = results.multi_hand_landmarks[1]

            # Draw landmarks
            mp_draw.draw_landmarks(img, hand1, mp_hands.HAND_CONNECTIONS)
            mp_draw.draw_landmarks(img, hand2, mp_hands.HAND_CONNECTIONS)

            # Get index finger tips and thumb tips
            index1 = hand1.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb1 = hand1.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index2 = hand2.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb2 = hand2.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convert coordinates to pixel values
            index1_x = int(index1.x * img.shape[1])
            index1_y = int(index1.y * img.shape[0])
            thumb1_x = int(thumb1.x * img.shape[1])
            thumb1_y = int(thumb1.y * img.shape[0])
            index2_x = int(index2.x * img.shape[1])
            index2_y = int(index2.y * img.shape[0])
            thumb2_x = int(thumb2.x * img.shape[1])
            thumb2_y = int(thumb2.y * img.shape[0])

            # Calculate the distances for pinch detection
            pinch1 = abs(index1_x - thumb1_x) < 40 and abs(index1_y - thumb1_y) < 40
            pinch2 = abs(index2_x - thumb2_x) < 40 and abs(index2_y - thumb2_y) < 40

            if pinch1 and pinch2:
                # Calculate the distance between the two index fingers
                distance = ((index2_x - index1_x) ** 2 + (index2_y - index1_y) ** 2) ** 0.5

                if initial_distance is None:
                    initial_distance = distance

                pinching = True
                zoom_factor = distance / initial_distance
                gesture_data = {"gesture": "pinch_zoom", "zoom_factor": zoom_factor}
            else:
                pinching = False

            if not pinching:
                initial_distance = None

    if not pinching:
        initial_distance = None

    # Write gesture data to a file
    with open('gesture_data.json', 'w') as f:
        json.dump(gesture_data, f)

    time.sleep(0.03)

cap.release()
