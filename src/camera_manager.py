"""Менеджер камер для работы с видеопотоками"""

import cv2
import time
from typing import List, Optional


class CameraManager:
    """Класс для управления камерами"""

    def __init__(self):
        self.cam1: Optional[cv2.VideoCapture] = None
        self.cam2: Optional[cv2.VideoCapture] = None

    @staticmethod
    def find_available_cameras() -> List[int]:
        """Находит все доступные камеры в системе"""
        available_cameras = []
        print('Поиск доступных камер...')

        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    available_cameras.append(i)
                    print(f'Найдена камера {i}')
                cap.release()
            time.sleep(0.1)

        print(f'Всего найдено камер: {len(available_cameras)}')
        return available_cameras

    def connect_camera(self, camera_number: int, camera_index: int) -> bool:
        """Подключение камеры"""
        from .config import CAMERA_WIDTH, CAMERA_HEIGHT

        # Освобождаем предыдущую камеру
        if camera_number == 1 and self.cam1:
            self.cam1.release()
        elif camera_number == 2 and self.cam2:
            self.cam2.release()

        # Подключаем новую камеру
        cam = cv2.VideoCapture(camera_index)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

        if cam.isOpened():
            if camera_number == 1:
                self.cam1 = cam
            else:
                self.cam2 = cam
            print(f'Камера {camera_number} подключена: индекс {camera_index}')
            return True
        else:
            cam.release()
            return False

    def read_frame(self, camera_number: int) -> tuple:
        """Чтение кадра с камеры"""
        cam = self.cam1 if camera_number == 1 else self.cam2
        if cam and cam.isOpened():
            return cam.read()
        return False, None

    def release_all(self):
        """Освобождение всех камер"""
        if self.cam1:
            self.cam1.release()
        if self.cam2:
            self.cam2.release()
        cv2.destroyAllWindows()
