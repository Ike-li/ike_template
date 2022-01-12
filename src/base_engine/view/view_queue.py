class ViewQueue:
    """
    view 管理队列
    """

    def __init__(self):
        self.queue = []

    def add(self, view):
        self.queue.append(view.get())

    def all(self):
        return self.queue
