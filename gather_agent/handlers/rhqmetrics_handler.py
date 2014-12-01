import rhqmetrics
from handler import Handler
from gather_event import Event

class RHQMetricsHandler(Handler):
    """
    This handler sends the events to the RHQ Metrics server
    """
    
    def __init__(self, config):
        self.config = config        
        self.r = rhqmetrics.RHQMetricsClient(config['rhqmetricshandler.host'], config['rhqmetricshandler.port'])

    def handle(self, item):
        self.r.put(item)

    def close(self):
        self.r.flush()
        
