import cv2
import mediapipe as mp
import numpy as np

mp_face = mp.solutions.face_mesh

class VideoClassifier:
    def __init__(self):
        self.face_mesh = mp_face.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def classify(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)

        if not result.multi_face_landmarks:
            return "NO_FACE", False  #  integrity

        landmarks = result.multi_face_landmarks[0].landmark

        nose = landmarks[1]
        left_eye = landmarks[33]
        right_eye = landmarks[263]

        dx = left_eye.x - right_eye.x
        dy = nose.y - ((left_eye.y + right_eye.y) / 2)

        # HEAD MOVEMENT LOGIC
        if abs(dx) > 0.05:
            return "HEAD_LEFT_RIGHT", False
        elif dy > 0.05:
            return "HEAD_DOWN", False
        elif dy < -0.05:
            return "HEAD_UP", False
        else:
            return "CENTER", True
