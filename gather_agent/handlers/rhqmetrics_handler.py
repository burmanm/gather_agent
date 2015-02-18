from rhqmetrics import *
from handler import Handler
from gather_event import Event

class RHQMetricsHandler(Handler):
    """
    This handler sends the events to the RHQ Metrics server
    """
    
    def __init__(self, config):
        self.config = config        
        self.r = RHQMetricsClient(config['rhqmetricshandler.tenant'],
                                  config['rhqmetricshandler.host'],
                                  config['rhqmetricshandler.port'],
        )

    def handle(self, items):
        batch = []

        if isinstance(items, list):
            for item in items:
                batch.append(self._get_metric_dict(item))
        else:
            batch.append(self._get_metric_dict(items))

        print batch
        self.r.put_multi(MetricType.Numeric, batch)

    def _get_metric_dict(self, item):
        metric_dict = self.r.create_metric_dict(item['value'], item['timestamp'])
        return self.r.create_data_dict(item['id'], [metric_dict])

    def close(self):
        pass
        
