from base_engine.view.view_queue import ViewQueue


class BaseController:

    def __init__(self, config):
        self.config = config

        self.message = []
        self.views = ViewQueue()

    def pre_action(self):
        pass

    def action(self):
        raise NotImplementedError

    def post_action(self):
        pass

    def update_config(self):
        raise NotImplementedError

    def run(self):
        self.pre_action()
        self.action()
        self.post_action()
        self.update_config()
