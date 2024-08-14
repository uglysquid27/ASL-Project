import cv2
import mediapipe as mp

# Initialize MediaPipe Hands and Face Detection
print("Initializing MediaPipe Hands and Face Detection...")
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection()
mp_draw = mp.solutions.drawing_utils

print("Accessing the webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the webcam.")
    exit()

print("Starting video capture...")
while cap.isOpened():
    success, img = cap.read()

    if not success:
        print("Error: Could not read a frame from the webcam.")
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_results = face_detection.process(img_rgb)
    hand_results = hands.process(img_rgb)

    head_center = None

    # Detect face and determine the head's center position
    if face_results.detections:
        for detection in face_results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, ic = img.shape
            head_center = (int(bboxC.xmin * iw + (bboxC.width * iw) / 2),
                           int(bboxC.ymin * ih + (bboxC.height * ih) / 2))

            # Draw the face detection box
            mp_draw.draw_detection(img, detection)

    if hand_results.multi_hand_landmarks and head_center is not None:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get the thumb, index, middle, ring, and pinky tips
            finger_tips = [hand_landmarks.landmark[i] for i in [4, 8, 12, 16, 20]]
            h, w, c = img.shape
            finger_tip_coords = [(int(lm.x * w), int(lm.y * h)) for lm in finger_tips]

            # Calculate distances from each fingertip to the head center
            distances = [(i, ((coord[0] - head_center[0]) ** 2 + (coord[1] - head_center[1]) ** 2) ** 0.5)
                         for i, coord in enumerate(finger_tip_coords)]

            # Sort fingers by distance
            distances.sort(key=lambda x: x[1])

            # If the thumb (index 0) is closer to the head than other fingers, assume the hand is facing the camera
            if distances[0][0] == 0:  # Thumb is closest to the head
                orientation = "Hand Facing Camera"
            else:
                orientation = "Hand Not Facing Camera"

            # Display the orientation on the image
            cv2.putText(img, orientation, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Optionally display the fingertip positions
            for idx, coord in enumerate(finger_tip_coords):
                cv2.putText(img, f'{idx}', coord, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.circle(img, head_center, 5, (255, 0, 0), cv2.FILLED)  # Mark the head center

    cv2.imshow("Hand and Face Tracking", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
