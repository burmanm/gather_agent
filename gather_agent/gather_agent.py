import Queue
import handlers
import inspect
import threading
import pkgutil
import os
import imp
from gatherer import Gatherer
import signal
import platform

class GatherAgent(object):

    def start(self):
        self.q = Queue.Queue()
        self.config = { 'interval': 15, 'prefix': platform.node() }
        self.gatherers = []

        # Start gatherers and handlers..
        self.client = handlers.RHQMetricsHandler(self.config)
        self.start_gatherers(self.load_gatherers_list(), self.client)

        signal.signal(signal.SIGINT, self._stop)
        self.active = True        
        
        self.loop()

    def start_gatherers(self, class_list, handler):
        for cls in class_list:
            instance = cls(handler, self.config, self.q)
            t = threading.Thread(target=instance.run)
            t.daemon = True
            t.start()
            self.gatherers.append(t)
        
    def loop(self):
        while self.active:
            event = self.q.get()
            event.handle()

    def load_gatherers_list(self):
        class_list = []

        path = os.path.join(os.path.dirname(__file__), "gatherers")
        modules = pkgutil.iter_modules(path=[path])

        for _, module_name, _ in modules:
            fp, pathname, description = imp.find_module(module_name, [path])
            module = imp.load_module(module_name, fp, pathname, description)
            for name in dir(module):
                o = getattr(module, name)
                if inspect.isclass(o) and issubclass(o, Gatherer) and o is not Gatherer:
                    class_list.append(o)
        return class_list

    def _stop(self, signum, frame):
        self.active = False
        for t in self.gatherers:
            t.close()

if __name__ == "__main__":
    g = GatherAgent()
    g.start()
