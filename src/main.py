# Plex API
import os
import threading

from workers.main_worker import MainWorker
from utils.folders import load_folders

worker = MainWorker()

started = False
start_lock = threading.Lock


def main():
    try:
        load_folders()
        worker.start()
        input("Press any enter to stop program...")
        worker.stop()
    except KeyboardInterrupt:
        pass
    worker.stop()


def start_django():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webui.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(["main.py", "runserver"])


if __name__ == "__main__":
    main()
