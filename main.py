import cv2
import os
import sys
import tkinter as tk
from tkinter import Button, Label, Entry, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import threading
import time

default_folder_to_save = "C:\\PhotoBook"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Функция для поиска доступных камер
def find_available_cameras():
    """Находит все доступные камеры в системе"""
    available_cameras = []
    print("Поиск доступных камер...")
    
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                available_cameras.append(i)
                print(f"Найдена камера {i}")
            cap.release()
        time.sleep(0.1)  # Небольшая пауза между проверками
    
    print(f"Всего найдено камер: {len(available_cameras)}")
    return available_cameras

class DualCameraApp:
    def __init__(self):
        self.cam1 = None
        self.cam2 = None
        self.captured_frame1 = None
        self.captured_frame2 = None
        self.is_running = False
        self.update_thread = None
        
        # БОЛЬШОЕ разрешение видео для хорошего качества
        self.video_size = 640  # Увеличено с 480 до 640 для лучшего качества
        
        # Настройка главного окна
        self.window = tk.Tk()
        self.window.title("Двойная веб-камера")
        try:
            icon_image = resource_path("icon.ico")
            self.window.iconbitmap(icon_image)
        except:
            pass
        
        self.setup_ui()
        self.setup_cameras()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        # Информационная панель
        info_frame = tk.Frame(self.window)
        info_frame.pack(pady=5)
        
        info_label = tk.Label(info_frame, text="Одновременный просмотр с двух камер", 
                             font=("Arial", 14, "bold"))
        info_label.pack()
        
        # ГЛАВНАЯ ПАНЕЛЬ: камеры + кнопки в одном ряду
        main_control_frame = tk.Frame(self.window)
        main_control_frame.pack(pady=10)
        
        # Левая часть - выбор камер
        cameras_frame = tk.Frame(main_control_frame)
        cameras_frame.pack(side='left', padx=10)
        
        # Первая камера
        cam1_frame = tk.Frame(cameras_frame, relief="ridge", bd=2)
        cam1_frame.pack(side='left', padx=10, pady=5)
        
        tk.Label(cam1_frame, text="Камера 1", font=("Arial", 12, "bold")).pack(pady=3)
        
        self.camera1_var = tk.StringVar()
        self.camera1_combo = ttk.Combobox(cam1_frame, textvariable=self.camera1_var, 
                                         state="readonly", width=15, font=("Arial", 10))
        self.camera1_combo.pack(pady=3)
        
        self.switch1_button = tk.Button(cam1_frame, text="Подключить", 
                                       command=self.switch_camera1, 
                                       relief="raised", bg="#90EE90", 
                                       font=("Arial", 9), width=12)
        self.switch1_button.pack(pady=3)
        
        # Статус первой камеры
        self.status1_label = tk.Label(cam1_frame, text="Не подключена", 
                                     fg="red", font=("Arial", 8))
        self.status1_label.pack()
        
        # Вторая камера
        cam2_frame = tk.Frame(cameras_frame, relief="ridge", bd=2)
        cam2_frame.pack(side='left', padx=10, pady=5)
        
        tk.Label(cam2_frame, text="Камера 2", font=("Arial", 12, "bold")).pack(pady=3)
        
        self.camera2_var = tk.StringVar()
        self.camera2_combo = ttk.Combobox(cam2_frame, textvariable=self.camera2_var, 
                                         state="readonly", width=15, font=("Arial", 10))
        self.camera2_combo.pack(pady=3)
        
        self.switch2_button = tk.Button(cam2_frame, text="Подключить", 
                                       command=self.switch_camera2, 
                                       relief="raised", bg="#90EE90", 
                                       font=("Arial", 9), width=12)
        self.switch2_button.pack(pady=3)
        
        # Статус второй камеры
        self.status2_label = tk.Label(cam2_frame, text="Не подключена", 
                                     fg="red", font=("Arial", 8))
        self.status2_label.pack()
        
        # ПРАВАЯ ЧАСТЬ - кнопки управления
        control_frame = tk.Frame(main_control_frame, relief="groove", bd=2)
        control_frame.pack(side='left', padx=20, pady=5)
        
        tk.Label(control_frame, text="Управление", font=("Arial", 12, "bold")).pack(pady=3)
        
        # Кнопки в компактном виде
        buttons_grid = tk.Frame(control_frame)
        buttons_grid.pack(pady=5)
        
        # Первая строка кнопок
        row1 = tk.Frame(buttons_grid)
        row1.pack(pady=2)
        
        self.start_button = tk.Button(row1, text="🎥 Запуск", 
                                     command=self.start_streaming, relief="raised", 
                                     bg="#87CEEB", font=("Arial", 9, "bold"),
                                     width=12, height=1)
        self.start_button.pack(side='left', padx=2)
        
        self.stop_button = tk.Button(row1, text="⏹ Стоп", 
                                    command=self.stop_streaming, relief="raised", 
                                    bg="#FFB6C1", font=("Arial", 9, "bold"),
                                    width=12, height=1)
        self.stop_button.pack(side='left', padx=2)
        
        # Вторая строка кнопок - УБИРАЕМ кнопку "Сохранить"
        row2 = tk.Frame(buttons_grid)
        row2.pack(pady=2)
        
        self.capture_button = tk.Button(row2, text="📸 Снимок", 
                                       command=self.capture_and_save_images, relief="raised", 
                                       bg="#FFD700", font=("Arial", 9, "bold"),
                                       width=25, height=1)  # Увеличиваем ширину
        self.capture_button.pack()
         
         # Убираем кнопку save_button полностью
        
        # Третья строка - закрыть
        row3 = tk.Frame(buttons_grid)
        row3.pack(pady=2)
        
        self.close_button = tk.Button(row3, text="❌ Закрыть", 
                                     command=self.close_app, relief="raised", 
                                     bg="#FF6B6B", font=("Arial", 9, "bold"),
                                     width=25, height=1)
        self.close_button.pack()
        
        # Панель видео с НОРМАЛЬНЫМ разрешением
        video_frame = tk.Frame(self.window)
        video_frame.pack(pady=15)
        
        # Контейнеры для видео с фиксированными минимальными размерами
        video1_container = tk.Frame(video_frame, relief="sunken", bd=3, width=660, height=660)
        video1_container.pack_propagate(False)  # Запрещаем изменение размера
        video1_container.pack(side='left', padx=15)
        
        tk.Label(video1_container, text="Камера 1", font=("Arial", 12, "bold")).pack(pady=3)
        self.video1_label = tk.Label(video1_container, bg="black", fg="white", 
                                     text="Камера 1\nне активна", font=("Arial", 12))
        self.video1_label.pack(expand=True)  # Заполняем весь контейнер
        
        video2_container = tk.Frame(video_frame, relief="sunken", bd=3, width=660, height=660)
        video2_container.pack_propagate(False)  # Запрещаем изменение размера
        video2_container.pack(side='left', padx=15)
        
        tk.Label(video2_container, text="Камера 2", font=("Arial", 12, "bold")).pack(pady=3)
        self.video2_label = tk.Label(video2_container, bg="black", fg="white", 
                                     text="Камера 2\nне активна", font=("Arial", 12))
        self.video2_label.pack(expand=True)  # Заполняем весь контейнер
        
        # Панель сохранения
        save_frame = tk.Frame(self.window)
        save_frame.pack(pady=10)
        
        tk.Label(save_frame, text="Папка для сохранения:", font=("Arial", 11)).pack()
        self.directory_entry = tk.Entry(save_frame, width=80, font=("Arial", 10))
        self.directory_entry.insert(0, default_folder_to_save)
        self.directory_entry.pack(pady=5)
        
        # Начальное состояние кнопок - убираем save_button
        self.stop_button.config(state='disabled')
        self.capture_button.config(state='disabled')
        
    def setup_cameras(self):
        """Настройка списка доступных камер"""
        available_cameras = find_available_cameras()
        
        camera_options = [f"Камера {i}" for i in available_cameras]
        if not camera_options:
            camera_options = ["Нет доступных камер"]
        
        self.camera1_combo['values'] = camera_options
        self.camera2_combo['values'] = camera_options
        
        # Устанавливаем значения по умолчанию
        if len(available_cameras) >= 1:
            self.camera1_combo.set(f"Камера {available_cameras[0]}")
        if len(available_cameras) >= 2:
            self.camera2_combo.set(f"Камера {available_cameras[1]}")
        elif len(available_cameras) >= 1:
            self.camera2_combo.set(f"Камера {available_cameras[0]}")
            
    def switch_camera1(self):
        """Подключение первой камеры"""
        selected = self.camera1_var.get()
        if "Камера" in selected:
            camera_index = int(selected.split()[-1])
            
            if self.cam1:
                self.cam1.release()
            
            self.cam1 = cv2.VideoCapture(camera_index)
            # Устанавливаем более высокое разрешение
            self.cam1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            if self.cam1.isOpened():
                self.status1_label.config(text="Подключена", fg="green")
                print(f"Камера 1 подключена: индекс {camera_index}")
            else:
                self.status1_label.config(text="Ошибка подключения", fg="red")
                self.cam1 = None
                
    def switch_camera2(self):
        """Подключение второй камеры"""
        selected = self.camera2_var.get()
        if "Камера" in selected:
            camera_index = int(selected.split()[-1])
            
            if self.cam2:
                self.cam2.release()
            
            self.cam2 = cv2.VideoCapture(camera_index)
            # Устанавливаем более высокое разрешение
            self.cam2.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam2.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            if self.cam2.isOpened():
                self.status2_label.config(text="Подключена", fg="green")
                print(f"Камера 2 подключена: индекс {camera_index}")
            else:
                self.status2_label.config(text="Ошибка подключения", fg="red")
                self.cam2 = None
                
    def process_frame(self, frame, size=None):
        """Обработка кадра для отображения"""
        if frame is None:
            return None
            
        if size is None:
            size = self.video_size
            
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
            
        resized_frame = cv2.resize(frame_rgb, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Создаем изображение фиксированного размера с черными полосами
        final_image = Image.new('RGB', (size, size), (0, 0, 0))
        pil_frame = Image.fromarray(resized_frame)
        
        # Центрируем изображение
        x = (size - new_width) // 2
        y = (size - new_height) // 2
        final_image.paste(pil_frame, (x, y))
        
        return final_image
        
    def update_frames(self):
        """Обновление кадров с обеих камер (выполняется в отдельном потоке)"""
        while self.is_running:
            try:
                # Обновляем первую камеру
                if self.cam1 and self.cam1.isOpened():
                    ret1, frame1 = self.cam1.read()
                    if ret1 and frame1 is not None:
                        processed_frame1 = self.process_frame(frame1)
                        if processed_frame1:
                            photo1 = ImageTk.PhotoImage(processed_frame1)
                            self.window.after(0, lambda: self.update_video_label(self.video1_label, photo1))
                    else:
                        self.window.after(0, lambda: self.video1_label.config(text="Камера 1\nне отвечает", image=""))
                
                # Обновляем вторую камеру
                if self.cam2 and self.cam2.isOpened():
                    ret2, frame2 = self.cam2.read()
                    if ret2 and frame2 is not None:
                        processed_frame2 = self.process_frame(frame2)
                        if processed_frame2:
                            photo2 = ImageTk.PhotoImage(processed_frame2)
                            self.window.after(0, lambda: self.update_video_label(self.video2_label, photo2))
                    else:
                        self.window.after(0, lambda: self.video2_label.config(text="Камера 2\nне отвечает", image=""))
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Ошибка в update_frames: {e}")
                time.sleep(0.1)
                
    def update_video_label(self, label, photo):
        """Безопасное обновление метки видео"""
        try:
            label.photo = photo  # Сохраняем ссылку
            label.config(image=photo, text="")
        except:
            pass
            
    def start_streaming(self):
        """Запуск трансляции"""
        if not self.cam1 and not self.cam2:
            messagebox.showwarning("Предупреждение", "Подключите хотя бы одну камеру!")
            return
            
        self.is_running = True
        self.update_thread = threading.Thread(target=self.update_frames, daemon=True)
        self.update_thread.start()
        
        # Обновляем состояние кнопок
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.capture_button.config(state='normal')
        
        print("Трансляция запущена")
        
    def stop_streaming(self):
        """Остановка трансляции"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
            
        # Очищаем дисплеи
        self.video1_label.config(text="Камера 1\nостановлена", image="")
        self.video2_label.config(text="Камера 2\nостановлена", image="")
        
        # Обновляем состояние кнопок
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.capture_button.config(state='disabled')
        
        print("Трансляция остановлена")
        
    def capture_and_save_images(self):
        """Захват и сохранение изображений с обеих камер одновременно"""
        captured_any = False
        
        # Временно меняем текст кнопки для индикации
        self.capture_button.config(text="📸 Сохраняем...", state='disabled')
        
        # Захват с первой камеры
        if self.cam1 and self.cam1.isOpened():
            ret1, frame1 = self.cam1.read()
            if ret1 and frame1 is not None:
                self.captured_frame1 = cv2.flip(frame1, 1)
                captured_any = True
                print("Снимок с камеры 1 сделан")
            else:
                self.captured_frame1 = None
                
        # Захват со второй камеры
        if self.cam2 and self.cam2.isOpened():
            ret2, frame2 = self.cam2.read()
            if ret2 and frame2 is not None:
                self.captured_frame2 = cv2.flip(frame2, 1)
                captured_any = True
                print("Снимок с камеры 2 сделан")
            else:
                self.captured_frame2 = None
                
        if captured_any:
            # Сразу сохраняем
            self.save_images_silent()
        else:
            # Возвращаем кнопку в исходное состояние
            self.capture_button.config(text="📸 Снимок", state='normal')
            print("Не удалось сделать снимки ни с одной камеры")
             
    def save_images_silent(self):
        """Сохранение изображений без лишних диалогов"""
        folder = self.directory_entry.get()
        if not os.path.exists(folder):
            self.capture_button.config(text="❌ Ошибка папки", bg="#FF6B6B")
            self.window.after(2000, lambda: self.capture_button.config(text="📸 Снимок", bg="#FFD700", state='normal'))
            return
             
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
         
        # Сохраняем изображение с первой камеры
        if self.captured_frame1 is not None:
            filename1 = f"{timestamp}_camera1.jpg"
            filepath1 = os.path.join(folder, filename1)
            cv2.imwrite(filepath1, self.captured_frame1)
            saved_files.append(filename1)
             
        # Сохраняем изображение со второй камеры
        if self.captured_frame2 is not None:
            filename2 = f"{timestamp}_camera2.jpg"
            filepath2 = os.path.join(folder, filename2)
            cv2.imwrite(filepath2, self.captured_frame2)
            saved_files.append(filename2)
             
        if saved_files:
            # Показываем успех через кнопку
            self.capture_button.config(text="✅ Сохранено!", bg="#98FB98")
            print(f"Сохранены файлы: {', '.join(saved_files)}")
             
            # Через 2 секунды возвращаем кнопку в исходное состояние
            self.window.after(2000, lambda: self.capture_button.config(text="📸 Снимок", bg="#FFD700", state='normal'))
             
            # Сброс захваченных кадров
            self.captured_frame1 = None
            self.captured_frame2 = None
            
    def close_app(self):
        """Закрытие приложения"""
        self.stop_streaming()
        
        if self.cam1:
            self.cam1.release()
        if self.cam2:
            self.cam2.release()
            
        cv2.destroyAllWindows()
        self.window.destroy()
        
    def run(self):
        """Запуск приложения"""
        self.window.minsize(1400, 900)  # Увеличиваем окно для больших видео
        self.window.mainloop()

# Запуск приложения
if __name__ == "__main__":
    app = DualCameraApp()
    app.run()

    
   
        