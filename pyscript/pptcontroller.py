
import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

mp_drawing = mp.solutions.drawing_utils

screen_width, screen_height = pyautogui.size()

cap = cv2.VideoCapture(0)
prev_x = None
prev_y = None
zoom_start_time = None
zoom_threshold = 100  # Adjust this value to control the zoom sensitivity

while cap.isOpened():
    ret, frame = cap.read()

    # mirror image
    frame = cv2.flip(frame, 1)

    # Convert to rgb
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            handedness = results.multi_handedness[results.multi_hand_landmarks.index(landmarks)].classification[0].label

            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

            index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_mid = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]

            if handedness == "Left":  # Navigate slides
                mcp_x = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x
                mcp_y = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y

                scaling_factor = 1  # Adjust this value to decrease sensitivity

                cursor_x = int(mcp_x * screen_width * scaling_factor)

                # Check for slide navigation
                if prev_x is not None:
                    dx = cursor_x - prev_x
                    if dx > 50:  # Slide right
                        pyautogui.hotkey('right')
                    elif dx < -50:  # Slide left
                        pyautogui.hotkey('left')

                prev_x = cursor_x

            elif handedness == "Right":  # Zoom in
                x, y = int(index_tip.x * screen_width), int(index_tip.y * screen_height)
                if prev_x is not None and prev_y is not None:
                    dx = x - prev_x
                    dy = y - prev_y

                    if abs(dx) < zoom_threshold and abs(dy) < zoom_threshold:
                        if zoom_start_time is None:
                            zoom_start_time = time.time()

                        if time.time() - zoom_start_time > 1:  # Zoom in gesture detected for 1 second
                            pyautogui.hotkey('ctrl', '+')

                    else:
                        zoom_start_time = None

                prev_x = x
                prev_y = y

    cv2.imshow("Gesture flow", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

