import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FaceTracker:
    """
    Rastreamento inteligente de rosto com MediaPipe para reenquadramento 9:16 (Shorts/TikTok).
    """
    def __init__(self, model_path: str = "models/face_detector.tflite", smoothing: float = 0.85):
        self.model_path = Path(model_path)
        self.smoothing = smoothing
        self.detector = None
        self._init_detector()

    def _init_detector(self):
        if not self.model_path.exists():
            print(f"[Tracker] Aviso: Modelo {self.model_path} não encontrado. Usando recorte central.")
            return

        base_options = python.BaseOptions(model_asset_path=str(self.model_path))
        options = vision.FaceDetectorOptions(base_options=base_options, min_detection_confidence=0.5)
        self.detector = vision.FaceDetector.create_from_options(options)

    def analyze_clip(self, video_path: Path, start_time: float, end_time: float, mode: str = "face_tracking") -> Dict[str, Any]:
        """
        Analisa o trecho do vídeo e calcula as coordenadas ideais de corte 9:16.
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir o vídeo: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        crop_h = height
        crop_w = int(height * 9 / 16)
        if crop_w % 2 != 0:
            crop_w -= 1
        if crop_w > width:
            crop_w = width

        # Se modo for centro ou detector não disponível
        if mode == "center" or self.detector is None:
            cap.release()
            center_x = max(0, int((width - crop_w) / 2))
            return {
                "mode": "center",
                "crop_w": crop_w,
                "crop_h": crop_h,
                "crop_x": center_x,
                "crop_y": 0,
                "width": width,
                "height": height,
                "ffmpeg_crop_filter": f"crop={crop_w}:{crop_h}:{center_x}:0,scale=1080:1920"
            }

        start_frame = max(0, int(start_time * fps))
        end_frame = min(total_frames, int(end_time * fps))
        duration_frames = end_frame - start_frame

        # Amostrar 3 a 5 frames por segundo para análise rápida
        sample_step = max(1, int(fps / 4))
        face_x_positions = []

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame

        while current_frame < end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            if (current_frame - start_frame) % sample_step == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                detection_result = self.detector.detect(mp_image)

                if detection_result.detections:
                    # Seleciona o rosto com maior área (locutor principal em foco)
                    best_detection = max(
                        detection_result.detections,
                        key=lambda d: d.bounding_box.width * d.bounding_box.height
                    )
                    bb = best_detection.bounding_box
                    face_center_x = bb.origin_x + bb.width / 2.0
                    face_x_positions.append(face_center_x)

            current_frame += 1

        cap.release()

        # Se nenhum rosto foi detectado na amostragem, usa o centro
        if not face_x_positions:
            print("[Tracker] Nenhum rosto detectado no trecho. Usando centro da tela.")
            target_x = max(0, int((width - crop_w) / 2))
        else:
            # Posição mediana do locutor no trecho para máxima estabilidade da câmera
            median_face_x = float(np.median(face_x_positions))
            target_x = int(median_face_x - crop_w / 2)
            # Garantir limites da tela
            target_x = max(0, min(target_x, width - crop_w))

        # Garantir número par para codecs de vídeo
        if target_x % 2 != 0:
            target_x = max(0, target_x - 1)

        print(f"[Tracker] Enquadramento calculado: X={target_x}, W={crop_w}, H={crop_h} (Original: {width}x{height})")

        return {
            "mode": mode,
            "crop_w": crop_w,
            "crop_h": crop_h,
            "crop_x": target_x,
            "crop_y": 0,
            "width": width,
            "height": height,
            "ffmpeg_crop_filter": f"crop={crop_w}:{crop_h}:{target_x}:0,scale=1080:1920"
        }
