from utils.folders import load_folders
from utils.logger import log
from workers.main_worker import MainWorker


def main():
    worker = None

    try:
        log("Loading folders...")
        load_folders()

        log("Launching...")
        worker = MainWorker()
        worker.start()

        input("Press any enter to stop program...\n")
    except KeyboardInterrupt:
        log("Closing...")

    if worker is not None:
        worker.stop()


if __name__ == "__main__":
    main()
