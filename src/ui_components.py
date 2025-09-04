"""Компоненты пользовательского интерфейса"""

import tkinter as tk
from tkinter import ttk
from typing import Callable
from .config import COLORS, VIDEO_CONTAINER_SIZE


class CameraSelector:
    """Виджет для выбора камеры"""

    def __init__(
        self,
        parent,
        camera_name: str,
        camera_options: list,
        switch_callback: Callable,
    ):
        self.frame = tk.Frame(parent, relief='ridge', bd=2)
        self.camera_var = tk.StringVar()
        self.switch_callback = switch_callback

        # Заголовок
        tk.Label(
            self.frame, text=camera_name, font=('Arial', 12, 'bold')
        ).pack(pady=3)

        # Выпадающий список
        self.combo = ttk.Combobox(
            self.frame,
            textvariable=self.camera_var,
            state='readonly',
            width=15,
            font=('Arial', 10),
        )
        self.combo['values'] = camera_options
        self.combo.pack(pady=3)

        # Кнопка подключения
        self.switch_button = tk.Button(
            self.frame,
            text='Подключить',
            command=self.switch_callback,
            relief='raised',
            bg=COLORS['connect'],
            font=('Arial', 9),
            width=12,
        )
        self.switch_button.pack(pady=3)

        # Статус
        self.status_label = tk.Label(
            self.frame, text='Не подключена', fg='red', font=('Arial', 8)
        )
        self.status_label.pack()

    def set_options(self, options: list):
        """Установка списка опций"""
        self.combo['values'] = options

    def set_value(self, value: str):
        """Установка выбранного значения"""
        self.combo.set(value)

    def get_value(self) -> str:
        """Получение выбранного значения"""
        return self.camera_var.get()

    def set_status(self, text: str, color: str):
        """Установка статуса"""
        self.status_label.config(text=text, fg=color)

    def pack(self, **kwargs):
        """Упаковка виджета"""
        self.frame.pack(**kwargs)


class VideoDisplay:
    """Виджет для отображения видео"""

    def __init__(self, parent, camera_name: str):
        self.container = tk.Frame(
            parent,
            relief='sunken',
            bd=3,
            width=VIDEO_CONTAINER_SIZE,
            height=VIDEO_CONTAINER_SIZE,
        )
        self.container.pack_propagate(False)

        # Заголовок
        tk.Label(
            self.container, text=camera_name, font=('Arial', 12, 'bold')
        ).pack(pady=3)

        # Видео метка
        self.video_label = tk.Label(
            self.container,
            bg='black',
            fg='white',
            text=f'{camera_name}\nне активна',
            font=('Arial', 12),
        )
        self.video_label.pack(expand=True)

    def update_image(self, photo):
        """Обновление изображения"""
        try:
            self.video_label.photo = photo
            self.video_label.config(image=photo, text='')
        except:
            pass

    def set_text(self, text: str):
        """Установка текста"""
        self.video_label.config(text=text, image='')

    def pack(self, **kwargs):
        """Упаковка виджета"""
        self.container.pack(**kwargs)


class ControlPanel:
    """Панель управления"""

    def __init__(self, parent, callbacks: dict):
        self.frame = tk.Frame(parent, relief='groove', bd=2)

        # Заголовок
        tk.Label(
            self.frame, text='Управление', font=('Arial', 12, 'bold')
        ).pack(pady=3)

        # Сетка кнопок
        buttons_grid = tk.Frame(self.frame)
        buttons_grid.pack(pady=5)

        # Первая строка кнопок
        row1 = tk.Frame(buttons_grid)
        row1.pack(pady=2)

        self.start_button = tk.Button(
            row1,
            text='🎥 Запуск',
            command=callbacks['start'],
            relief='raised',
            bg=COLORS['info'],
            font=('Arial', 9, 'bold'),
            width=12,
            height=1,
        )
        self.start_button.pack(side='left', padx=2)

        self.stop_button = tk.Button(
            row1,
            text='⏹ Стоп',
            command=callbacks['stop'],
            relief='raised',
            bg=COLORS['stop'],
            font=('Arial', 9, 'bold'),
            width=12,
            height=1,
        )
        self.stop_button.pack(side='left', padx=2)

        # Вторая строка - снимок
        row2 = tk.Frame(buttons_grid)
        row2.pack(pady=2)

        self.capture_button = tk.Button(
            row2,
            text='📸 Снимок',
            command=callbacks['capture'],
            relief='raised',
            bg=COLORS['warning'],
            font=('Arial', 9, 'bold'),
            width=25,
            height=1,
        )
        self.capture_button.pack()

        # Третья строка - закрыть
        row3 = tk.Frame(buttons_grid)
        row3.pack(pady=2)

        self.close_button = tk.Button(
            row3,
            text='❌ Закрыть',
            command=callbacks['close'],
            relief='raised',
            bg=COLORS['error'],
            font=('Arial', 9, 'bold'),
            width=25,
            height=1,
        )
        self.close_button.pack()

        # Начальное состояние
        self.stop_button.config(state='disabled')
        self.capture_button.config(state='disabled')

    def set_streaming_state(self, is_streaming: bool):
        """Установка состояния трансляции"""
        if is_streaming:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.capture_button.config(state='normal')
        else:
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.capture_button.config(state='disabled')

    def set_capture_status(self, status: str):
        """Установка статуса захвата"""
        if status == 'saving':
            self.capture_button.config(
                text='📸 Сохраняем...', state='disabled'
            )
        elif status == 'success':
            self.capture_button.config(
                text='✅ Сохранено!', bg=COLORS['success']
            )
        elif status == 'error':
            self.capture_button.config(text='❌ Ошибка', bg=COLORS['error'])
        elif status == 'normal':
            self.capture_button.config(
                text='📸 Снимок', bg=COLORS['warning'], state='normal'
            )

    def pack(self, **kwargs):
        """Упаковка виджета"""
        self.frame.pack(**kwargs)
