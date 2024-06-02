class Startable:

    def __init__(self):
        self.is_running = False

    def start(self):
        self.is_running = True
        self.on_start()
        self.started()

    def started(self):
        pass

    def stop(self):
        self.is_running = False
        self.on_stop()
        self.stopped()

    def stopped(self):
        pass

    def on_start(self):
        pass

    def on_stop(self):
        pass
