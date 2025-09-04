"""Управление файлами и сохранением"""

import os
import cv2
from datetime import datetime
from typing import List, Optional


class FileManager:
    """Класс для работы с файлами"""

    @staticmethod
    def ensure_directory_exists(path: str) -> bool:
        """Создает директорию, если её нет"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f'Ошибка создания папки: {e}')
            return False

    @staticmethod
    def save_image(frame, folder: str, camera_number: int) -> Optional[str]:
        """Сохранение изображения"""
        if frame is None:
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{timestamp}_camera{camera_number}.jpg'
        filepath = os.path.join(folder, filename)

        try:
            cv2.imwrite(filepath, frame)
            return filename
        except Exception as e:
            print(f'Ошибка сохранения файла: {e}')
            return None

    @staticmethod
    def save_images(frame1, frame2, folder: str) -> List[str]:
        """Сохранение изображений с обеих камер"""
        saved_files = []

        if not FileManager.ensure_directory_exists(folder):
            return saved_files

        # Сохраняем изображение с первой камеры
        if frame1 is not None:
            filename1 = FileManager.save_image(frame1, folder, 1)
            if filename1:
                saved_files.append(filename1)

        # Сохраняем изображение со второй камеры
        if frame2 is not None:
            filename2 = FileManager.save_image(frame2, folder, 2)
            if filename2:
                saved_files.append(filename2)

        return saved_files
