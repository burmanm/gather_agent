class Event(object):
    """
        Simple Event fired by the different gatherers
    """
    def __init__(self, handler, data):
        self.handler = handler
        self.data = data

    def handle(self):
        self.handler.handle(self.data)
