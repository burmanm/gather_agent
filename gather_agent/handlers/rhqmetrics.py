import rhqmetricsclient
from handler import Handler
from gatherEvent import Event

class RHQMetricsHandler(Handler):

    def __init__(self, config):
        self.config = config
        self.r = rhqmetricsclient.RHQMetricsClient()

    """description of class"""
    def handle(self, item):
        if not isinstance(item, list):
            ls = []
            ls.append(item)
            item = ls

        self.r.put_batch(item)
