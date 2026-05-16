import cv2

def start_eye_tracking():
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    smile_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_smile.xml"
    )
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_eye.xml"
    )

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        caption = "No Face Detected"

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            roi_gray = gray[y:y+h, x:x+w]

            smiles = smile_cascade.detectMultiScale(
                roi_gray, scaleFactor=1.8, minNeighbors=20
            )
            eyes = eye_cascade.detectMultiScale(
                roi_gray, scaleFactor=1.1, minNeighbors=10
            )

            face_center = x + w // 2
            frame_center = frame.shape[1] // 2

            if face_center < frame_center - 40:
                caption = "Looking Left"
            elif face_center > frame_center + 40:
                caption = "Looking Right"
            else:
                caption = "Looking Center"

            if len(smiles) > 0:
                caption = "Smile Detected"

        cv2.putText(
            frame,
            caption,
            (30, frame.shape[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.imshow("Interview Eye Tracking", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            break

    cap.release()
    cv2.destroyAllWindows()
