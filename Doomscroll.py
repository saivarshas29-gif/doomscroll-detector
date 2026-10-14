import cv2
import time
import pygame
from ultralytics import YOLO

import os
import sys

# 1. Initialize Pygame Audio Mixer
pygame.mixer.init()
alarm_loaded = False
sound_candidates = ["alarm.mp3", "alarm.mp3.mp3", "alarm.wav"]
sound_file = next((f for f in sound_candidates if os.path.exists(f)), None)

if sound_file:
    try:
        pygame.mixer.music.load(sound_file)
        alarm_loaded = True
        print(f"Loaded alarm sound: {sound_file}")
    except Exception as e:
        print(f"[Warning] Could not load alarm sound: {e}")
else:
    print("[Warning] No sound file found. Will use system beep fallback.")

# 2. Load YOLOv8 Small model (significantly better at angled / slanting phones than Nano)
# COCO dataset Class 67 is 'cell phone', 65 is 'remote'
model = YOLO("yolov8s.pt")

# 3. Start Webcam Stream (0 is usually the default web camera)
cap = cv2.VideoCapture(0)
# Request HD resolution (1280x720) so thin edges of slanting phones are clearer
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Settings & Debounce Timers
PHONE_CLASSES = {67: "Phone", 65: "Remote/Phone"}  # COCO indexes
CONFIDENCE_THRESHOLD = 0.22  # Tuned lower for slanting/tilted orientations
DETECTION_DELAY = 1.5        # Seconds of holding phone before triggering alarm
GRACE_PERIOD = 1.0           # Seconds of buffer before resetting timer (prevents angle flicker)

phone_detected_start_time = None
last_seen_time = 0
alarm_active = False

print("\n--- Doomscroll Detector Running ---")
print("Press 'q' in the camera window to quit.\n")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame from camera.")
        break

    # Run YOLO inference on the current frame
    results = model(frame, verbose=False)[0]
    
    phone_found = False

    # Check detected bounding boxes
    for box in results.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        if class_id in PHONE_CLASSES and confidence >= CONFIDENCE_THRESHOLD:
            phone_found = True
            label = f"{PHONE_CLASSES[class_id]} ({confidence:.2f})"
            
            # Draw bounding box around the phone
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(
                frame, 
                label, 
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                (0, 0, 255), 
                2
            )

    # State Machine Logic with Grace Period (handles flickering/angles)
    current_time = time.time()

    if phone_found:
        last_seen_time = current_time
        if phone_detected_start_time is None:
            phone_detected_start_time = current_time

    if phone_detected_start_time is not None:
        # Check if still within grace period
        if (current_time - last_seen_time) <= GRACE_PERIOD:
            elapsed_time = current_time - phone_detected_start_time

            # Show holding progress on screen
            if not alarm_active:
                cv2.putText(
                    frame,
                    f"Phone detected: {elapsed_time:.1f}s / {DETECTION_DELAY}s",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 165, 255),
                    2
                )

            # Trigger alarm if phone is held longer than the threshold
            if elapsed_time >= DETECTION_DELAY:
                alarm_active = True
                if alarm_loaded:
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(-1)  # Play in a continuous loop
                elif sys.platform == "win32":
                    import winsound
                    winsound.Beep(1200, 200)
                
                # Flash visual alert overlay on the video feed
                cv2.putText(
                    frame, 
                    "DOOMSCROLLING DETECTED! PUT IT DOWN!", 
                    (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.9, 
                    (0, 0, 255), 
                    3
                )
        else:
            # Grace period expired: phone put down
            phone_detected_start_time = None
            if alarm_active:
                alarm_active = False
                if alarm_loaded:
                    pygame.mixer.music.stop()

    # Display video feed
    cv2.imshow("Doomscroll Detector", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup resources
cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()