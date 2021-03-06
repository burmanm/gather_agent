import time
from gather_event import Event

class Gatherer(object):
    """
    Abstract class for different gathering plugins
    Can return a list of events or a single item
    """
    def __init__(self, handler, config, q):
        self.q = q
        self.config = config
        self.interval = float(config['interval'])
        self.handler = handler
        self.active = True
        self.init(self.config)

    def gather(self):
        """
        The function that returns an event or a list of events. Must be overridden
        in the extending class.
        """
        raise NotImplementedError()

    def init(self, config):
        """
        Init method for the objects that extend Gatherer. By default does
        not do anything.
        """
        pass

    def create_event(self, key, value, timestamp=None):
        """
        Returns a new Event based on the key and value, and creates a timestamp to the
        object. A key that is created is formatted with hostname.class_name.key 
        """
        if timestamp is None:
            timestamp = int(round(time.time() * 1000))
            
        prefixed_key = "{0}.{1}.{2}".format(self.config['prefix'], self.__class__.__name__, key)
        item = { 'id': prefixed_key,
                 'timestamp': timestamp,
                 'value': float(value)}
        return item

    def run(self):
        """
        The threading method, that will be active in the background
        """
        while self.active:
            item = self.gather()
            if item is not None:
                event = Event(self.handler, item)
                self.q.put(event)
            time.sleep(self.interval)
        return

    def close(self):
        # Interrupt main thread? Otherwise this will unfortunately wait until interval has passed..
        self.active = False       
        return
