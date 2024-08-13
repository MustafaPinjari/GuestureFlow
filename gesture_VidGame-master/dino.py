import cv2
import mediapipe as mp
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

tipIds = [4, 8, 12, 16, 20]
minAngle = 0
maxAngle = 255
angle = 0
angleBar = 400
angleDeg = 0
minHand = 50
maxHand = 300
status = "Normal"

def findHands(image, draw=True):
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            if draw:
                mp_drawing.draw_landmarks(image, handLms, mp_hands.HAND_CONNECTIONS)
    return image

def fingerPosition(image, handNo=0, draw=True):
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])
            if draw:
                cv2.circle(image, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
    return lmList

cap = cv2.VideoCapture(0)
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, image = cap.read()
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        lmList = fingerPosition(image)
        if len(lmList) != 0:
            fingers = []
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                if lmList[tipIds[id]][2] > lmList[tipIds[id] - 2][2]:
                    fingers.append(0)
            totalFingers = fingers.count(1)

            if totalFingers == 0:
                pyautogui.press('space')
                status = "Jump"
            else:
                status = "Run"
            cv2.putText(image, status, (40, 100), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)

        cv2.imshow("Hand Landmark", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
