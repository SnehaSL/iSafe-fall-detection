import cv2
import mediapipe as mp
import time

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Initialize Webcam
cap = cv2.VideoCapture(1)

# Initialize variables for posture accumulation
posture_accumulation = []
start_time = time.time()
accumulation_interval = 2  # seconds
display_duration = 5  # seconds
last_majority_posture = None
last_majority_start_time = 0

while True:
    success, img = cap.read()

    # Convert the BGR image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the image with MediaPipe Pose
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        # Extract landmarks for key points
        landmarks = results.pose_landmarks.landmark
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]

        # Calculate the angle between the hips and knees
        angle_hip_knee_left = abs(left_hip.y - left_knee.y)
        angle_hip_knee_right = abs(right_hip.y - right_knee.y)

        # Set a threshold for sitting detection
        sit_threshold = 0.1  # You may need to adjust this based on your specific scenario

        # Check if the person is sitting
        if angle_hip_knee_left < sit_threshold and angle_hip_knee_right < sit_threshold:
            status = "Sitting"
        else:
            status = "Standing"

        # Draw landmarks on the image
        mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.putText(img, f"Status: {status}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        # Record the posture for accumulation
        posture_accumulation.append(status)

        # Check if accumulation interval is reached
        elapsed_time = time.time() - start_time
        if elapsed_time >= accumulation_interval:
            # Determine the majority posture
            majority_posture = max(set(posture_accumulation), key=posture_accumulation.count)

            # Check if the majority posture has changed
            if majority_posture != last_majority_posture:
                last_majority_posture = majority_posture
                last_majority_start_time = time.time()

            # Check if the display duration has passed since the last majority change
            elapsed_display_time = time.time() - last_majority_start_time
            if elapsed_display_time <= display_duration:
                # Display the majority posture
                cv2.putText(img, f"Majority: {last_majority_posture}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # Reset accumulation variables
                posture_accumulation = []
                start_time = time.time()

    cv2.imshow("Body Posture Detection", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
