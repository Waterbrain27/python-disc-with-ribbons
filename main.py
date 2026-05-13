"""Точка входа в приложение. Создаёт и запускает экземпляр Application."""

from app import Application


if __name__ == "__main__":
    """
    Запуск приложения.
    Создаётся объект Application, после чего вызывается его метод run().
    Вся инициализация и основной цикл выполняются внутри app.py.
    """
    app = Application()
    app.run()