import os
import sys
import time
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pygame
from ultralytics import YOLO

# Resolve base directory so script works regardless of execution working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@lru_cache(maxsize=16)
def get_font(size, bold=True):
    """Loads and caches a clean, modern system font (Segoe UI or Arial) with fallback."""
    font_names = (
        ["segoeuib.ttf", "arialbd.ttf", "impact.ttf"]
        if bold
        else ["segoeui.ttf", "arial.ttf"]
    )
    windir = os.environ.get("WINDIR", "C:\\Windows")
    for name in font_names:
        path = os.path.join(windir, "Fonts", name)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_centered_alert(frame, main_text, sub_text=None):
    """Draws a beautiful, modern centered alert card with large crisp typography."""
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2

    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil, "RGBA")

    font_main = get_font(46, bold=True)
    font_sub = get_font(26, bold=False)

    card_w = min(920, w - 40)
    card_h = 170 if sub_text else 120
    x1 = cx - card_w // 2
    y1 = cy - card_h // 2
    x2 = cx + card_w // 2
    y2 = cy + card_h // 2

    # Semi-transparent dark frosted glass card with vivid crimson/red border
    draw.rounded_rectangle(
        [(x1, y1), (x2, y2)],
        radius=20,
        fill=(18, 18, 24, 220),
        outline=(255, 59, 48, 240),
        width=3,
    )

    if sub_text:
        main_y = cy - 28
        sub_y = cy + 34
    else:
        main_y = cy
        sub_y = None

    # Main Alert: Large, vibrant alert red/coral
    draw.text((cx, main_y), main_text, font=font_main, fill=(255, 75, 75), anchor="mm")

    # Subtext: Clean bright white
    if sub_text:
        draw.text((cx, sub_y), sub_text, font=font_sub, fill=(245, 245, 245), anchor="mm")

    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def draw_progress_badge(frame, elapsed_time, delay):
    """Draws a sleek top-centered pill badge showing holding progress."""
    h, w = frame.shape[:2]
    cx = w // 2

    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil, "RGBA")
    font = get_font(22, bold=True)

    text = f"Phone detected: {elapsed_time:.1f}s / {delay:.1f}s"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pw, ph = tw + 40, th + 20
    x1, y1 = cx - pw // 2, 20
    x2, y2 = cx + pw // 2, 20 + ph

    # Top pill with amber glow
    draw.rounded_rectangle(
        [(x1, y1), (x2, y2)],
        radius=14,
        fill=(20, 20, 25, 210),
        outline=(255, 170, 0, 230),
        width=2,
    )
    draw.text((cx, 20 + ph // 2), text, font=font, fill=(255, 185, 35), anchor="mm")

    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def main():
    # 1. Initialize Pygame Audio Mixer
    pygame.mixer.init()
    alarm_loaded = False
    sound_candidates = [
        os.path.join(BASE_DIR, "alarm.mp3"),
        os.path.join(BASE_DIR, "alarm.wav"),
    ]
    sound_file = next((f for f in sound_candidates if os.path.exists(f)), None)

    if sound_file:
        try:
            pygame.mixer.music.load(sound_file)
            alarm_loaded = True
            print(f"Loaded alarm sound: {os.path.basename(sound_file)}")
        except Exception as e:
            print(f"[Warning] Could not load alarm sound: {e}")
    else:
        print("[Warning] No sound file found. Will use system beep fallback.")

    # 2. Load YOLOv8 Small model (significantly better at angled / slanting phones than Nano)
    model_path = os.path.join(BASE_DIR, "yolov8s.pt")
    model = YOLO(model_path if os.path.exists(model_path) else "yolov8s.pt")

    # 3. Start Webcam Stream (0 is usually the default web camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("\n[Error] Could not open webcam (index 0).")
        print("Please make sure your camera is connected and not currently used by another application.\n")
        return

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
    print("Press 'q' in the camera window (or click 'X') to quit.\n")

    try:
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
                        frame = draw_progress_badge(frame, elapsed_time, DETECTION_DELAY)

                    # Trigger alarm if phone is held longer than the threshold
                    if elapsed_time >= DETECTION_DELAY:
                        alarm_active = True
                        if alarm_loaded:
                            if not pygame.mixer.music.get_busy():
                                pygame.mixer.music.play(-1)  # Play in a continuous loop
                        elif sys.platform == "win32":
                            import winsound
                            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                        
                        # Big, modern, centered alert overlay
                        frame = draw_centered_alert(
                            frame, 
                            main_text="DOOMSCROLLING DETECTED!", 
                            sub_text="PUT YOUR PHONE DOWN!"
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

            # Check if user pressed 'q' or closed the window via 'X' button
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if cv2.getWindowProperty("Doomscroll Detector", cv2.WND_PROP_VISIBLE) < 1:
                break

    finally:
        # Cleanup resources safely
        cap.release()
        cv2.destroyAllWindows()
        if alarm_loaded:
            pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("Doomscroll Detector closed safely.")


if __name__ == "__main__":
    main()