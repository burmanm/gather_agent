import rhqmetrics
from handler import Handler
from gatherEvent import Event

class RHQMetricsHandler(Handler):
    """
    This handler sends the events to the RHQ Metrics server
    """
    
    def __init__(self, config):
        self.config = config
        self.r = rhqmetrics.RHQMetricsClient()

    def handle(self, item):
        self.r.put(item)

    def close(self):
        self.r.flush()
        
