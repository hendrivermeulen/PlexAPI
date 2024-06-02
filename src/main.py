from utils.folders import load_folders
from workers.main_worker import MainWorker

worker = MainWorker()


def main():
    try:
        load_folders()
        worker.start()
        input("Press any enter to stop program...\n")
    except KeyboardInterrupt:
        pass
    worker.stop()


if __name__ == "__main__":
    main()
