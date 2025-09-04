"""Главное приложение двойной камеры"""

import tkinter as tk
from tkinter import messagebox, Entry, Label
import threading
import time
from PIL import ImageTk

from .config import *
from .camera_manager import CameraManager
from .image_processor import ImageProcessor
from .file_manager import FileManager
from .ui_components import CameraSelector, VideoDisplay, ControlPanel
from .utils import resource_path


class DualCameraApp:
    """Главный класс приложения"""

    def __init__(self):
        self.camera_manager = CameraManager()
        self.image_processor = ImageProcessor()
        self.file_manager = FileManager()

        self.captured_frame1 = None
        self.captured_frame2 = None
        self.is_running = False
        self.update_thread = None

        self.setup_window()
        self.setup_ui()
        self.setup_cameras()

    def setup_window(self):
        """Настройка главного окна"""
        self.window = tk.Tk()
        self.window.title('Двойная веб-камера')

        try:
            icon_image = resource_path('icon.ico')
            self.window.iconbitmap(icon_image)
        except:
            pass

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""

        # Заголовок
        info_frame = tk.Frame(self.window)
        info_frame.pack(pady=5)

        tk.Label(
            info_frame,
            text='Одновременный просмотр с двух камер',
            font=('Arial', 14, 'bold'),
        ).pack()

        # Главная панель управления
        main_control_frame = tk.Frame(self.window)
        main_control_frame.pack(pady=10)

        # Левая часть - выбор камер
        cameras_frame = tk.Frame(main_control_frame)
        cameras_frame.pack(side='left', padx=10)

        # Селекторы камер
        self.camera1_selector = CameraSelector(
            cameras_frame, 'Камера 1', [], self.switch_camera1
        )
        self.camera1_selector.pack(side='left', padx=10, pady=5)

        self.camera2_selector = CameraSelector(
            cameras_frame, 'Камера 2', [], self.switch_camera2
        )
        self.camera2_selector.pack(side='left', padx=10, pady=5)

        # Правая часть - управление
        self.control_panel = ControlPanel(
            main_control_frame,
            {
                'start': self.start_streaming,
                'stop': self.stop_streaming,
                'capture': self.capture_and_save_images,
                'close': self.close_app,
            },
        )
        self.control_panel.pack(side='left', padx=20, pady=5)

        # Панель видео
        video_frame = tk.Frame(self.window)
        video_frame.pack(pady=15)

        self.video1_display = VideoDisplay(video_frame, 'Камера 1')
        self.video1_display.pack(side='left', padx=15)

        self.video2_display = VideoDisplay(video_frame, 'Камера 2')
        self.video2_display.pack(side='left', padx=15)

        # Панель сохранения
        save_frame = tk.Frame(self.window)
        save_frame.pack(pady=10)

        Label(
            save_frame, text='Папка для сохранения:', font=('Arial', 11)
        ).pack()
        self.directory_entry = Entry(save_frame, width=80, font=('Arial', 10))
        self.directory_entry.insert(0, DEFAULT_SAVE_FOLDER)
        self.directory_entry.pack(pady=5)

    def setup_cameras(self):
        """Настройка списка доступных камер"""
        available_cameras = CameraManager.find_available_cameras()
        camera_options = [f'Камера {i}' for i in available_cameras]

        if not camera_options:
            camera_options = ['Нет доступных камер']

        self.camera1_selector.set_options(camera_options)
        self.camera2_selector.set_options(camera_options)

        # Устанавливаем значения по умолчанию
        if len(available_cameras) >= 1:
            self.camera1_selector.set_value(f'Камера {available_cameras[0]}')
        if len(available_cameras) >= 2:
            self.camera2_selector.set_value(f'Камера {available_cameras[1]}')
        elif len(available_cameras) >= 1:
            self.camera2_selector.set_value(f'Камера {available_cameras[0]}')

    def switch_camera1(self):
        """Подключение первой камеры"""
        selected = self.camera1_selector.get_value()
        if 'Камера' in selected:
            camera_index = int(selected.split()[-1])

            if self.camera_manager.connect_camera(1, camera_index):
                self.camera1_selector.set_status('Подключена', 'green')
            else:
                self.camera1_selector.set_status('Ошибка подключения', 'red')

    def switch_camera2(self):
        """Подключение второй камеры"""
        selected = self.camera2_selector.get_value()
        if 'Камера' in selected:
            camera_index = int(selected.split()[-1])

            if self.camera_manager.connect_camera(2, camera_index):
                self.camera2_selector.set_status('Подключена', 'green')
            else:
                self.camera2_selector.set_status('Ошибка подключения', 'red')

    def update_frames(self):
        """Обновление кадров с обеих камер"""
        while self.is_running:
            try:
                # Обновляем первую камеру
                ret1, frame1 = self.camera_manager.read_frame(1)
                if ret1 and frame1 is not None:
                    processed_frame1 = self.image_processor.process_frame(
                        frame1, VIDEO_SIZE
                    )
                    if processed_frame1:
                        photo1 = ImageTk.PhotoImage(processed_frame1)
                        self.window.after(
                            0, lambda: self.video1_display.update_image(photo1)
                        )
                else:
                    self.window.after(
                        0,
                        lambda: self.video1_display.set_text(
                            'Камера 1\nне отвечает'
                        ),
                    )

                # Обновляем вторую камеру
                ret2, frame2 = self.camera_manager.read_frame(2)
                if ret2 and frame2 is not None:
                    processed_frame2 = self.image_processor.process_frame(
                        frame2, VIDEO_SIZE
                    )
                    if processed_frame2:
                        photo2 = ImageTk.PhotoImage(processed_frame2)
                        self.window.after(
                            0, lambda: self.video2_display.update_image(photo2)
                        )
                else:
                    self.window.after(
                        0,
                        lambda: self.video2_display.set_text(
                            'Камера 2\nне отвечает'
                        ),
                    )

                time.sleep(1.0 / FPS)

            except Exception as e:
                print(f'Ошибка в update_frames: {e}')
                time.sleep(0.1)

    def start_streaming(self):
        """Запуск трансляции"""
        if not self.camera_manager.cam1 and not self.camera_manager.cam2:
            messagebox.showwarning(
                'Предупреждение', 'Подключите хотя бы одну камеру!'
            )
            return

        self.is_running = True
        self.update_thread = threading.Thread(
            target=self.update_frames, daemon=True
        )
        self.update_thread.start()

        self.control_panel.set_streaming_state(True)
        print('Трансляция запущена')

    def stop_streaming(self):
        """Остановка трансляции"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)

        self.video1_display.set_text('Камера 1\nостановлена')
        self.video2_display.set_text('Камера 2\nостановлена')

        self.control_panel.set_streaming_state(False)
        print('Трансляция остановлена')

    def capture_and_save_images(self):
        """Захват и сохранение изображений"""
        self.control_panel.set_capture_status('saving')

        captured_any = False

        # Захват с первой камеры
        ret1, frame1 = self.camera_manager.read_frame(1)
        if ret1 and frame1 is not None:
            self.captured_frame1 = self.image_processor.prepare_for_save(
                frame1
            )
            captured_any = True
            print('Снимок с камеры 1 сделан')
        else:
            self.captured_frame1 = None

        # Захват со второй камеры
        ret2, frame2 = self.camera_manager.read_frame(2)
        if ret2 and frame2 is not None:
            self.captured_frame2 = self.image_processor.prepare_for_save(
                frame2
            )
            captured_any = True
            print('Снимок с камеры 2 сделан')
        else:
            self.captured_frame2 = None

        if captured_any:
            self.save_images()
        else:
            self.control_panel.set_capture_status('normal')
            print('Не удалось сделать снимки ни с одной камеры')

    def save_images(self):
        """Сохранение изображений"""
        folder = self.directory_entry.get()

        saved_files = self.file_manager.save_images(
            self.captured_frame1, self.captured_frame2, folder
        )

        if saved_files:
            self.control_panel.set_capture_status('success')
            print(f'Сохранены файлы: {", ".join(saved_files)}')

            # Возврат к нормальному состоянию через 2 секунды
            self.window.after(
                2000, lambda: self.control_panel.set_capture_status('normal')
            )
        else:
            self.control_panel.set_capture_status('error')
            self.window.after(
                2000, lambda: self.control_panel.set_capture_status('normal')
            )

        # Сброс захваченных кадров
        self.captured_frame1 = None
        self.captured_frame2 = None

    def close_app(self):
        """Закрытие приложения"""
        self.stop_streaming()
        self.camera_manager.release_all()
        self.window.destroy()

    def run(self):
        """Запуск приложения"""
        self.window.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.window.mainloop()
