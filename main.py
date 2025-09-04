"""
Точка входа в приложение двойной камеры
Структурированная версия с разделением по модулям
"""

from src.dual_camera_app import DualCameraApp


def main():
    """Главная функция запуска приложения"""
    try:
        app = DualCameraApp()
        app.run()
    except KeyboardInterrupt:
        print('Приложение закрыто пользователем')
    except Exception as e:
        print(f'Ошибка запуска приложения: {e}')


if __name__ == '__main__':
    main()
