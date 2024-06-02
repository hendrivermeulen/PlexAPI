# Plex API
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

if __name__ == "__main__":
    main()
