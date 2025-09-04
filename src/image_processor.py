"""Обработка изображений с камер"""

import cv2
from PIL import Image
from typing import Optional


class ImageProcessor:
    """Класс для обработки изображений"""

    @staticmethod
    def process_frame(frame, size: int = 640) -> Optional[Image.Image]:
        """Обработка кадра для отображения"""
        if frame is None:
            return None

        # Отражаем кадр горизонтально
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Изменяем размер с сохранением пропорций
        h, w = frame_rgb.shape[:2]
        aspect_ratio = w / h

        if aspect_ratio > 1:  # Широкий формат
            new_width = size
            new_height = int(size / aspect_ratio)
        else:  # Высокий формат
            new_height = size
            new_width = int(size * aspect_ratio)

        resized_frame = cv2.resize(
            frame_rgb,
            (new_width, new_height),
            interpolation=cv2.INTER_LANCZOS4,
        )

        # Создаем изображение фиксированного размера с черными полосами
        final_image = Image.new('RGB', (size, size), (0, 0, 0))
        pil_frame = Image.fromarray(resized_frame)

        # Центрируем изображение
        x = (size - new_width) // 2
        y = (size - new_height) // 2
        final_image.paste(pil_frame, (x, y))

        return final_image

    @staticmethod
    def prepare_for_save(frame) -> Optional[any]:
        """Подготовка кадра для сохранения"""
        if frame is None:
            return None
        return cv2.flip(frame, 1)
