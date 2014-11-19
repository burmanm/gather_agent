import Queue
import handlers
import gatherers
import inspect
import threading
import platform
import pkgutil
import os

class GatherAgent(object):

    def start(self):
        self.q = Queue.Queue()
        self.config = { 'interval': 15, 'prefix': platform.node() }
        self.gatherers = []

        # Start gatherers and handlers..
        self.client = handlers.RHQMetricsHandler(self.config)
        self.start_gatherers(self.load_gatherers_list(), self.client)
        
        self.loop()

    def start_gatherers(self, class_list, handler):
        for cls in class_list:
            instance = cls(handler, self.config, self.q)
            t = threading.Thread(target=instance.run)
            t.daemon = True
            t.start()
            self.gatherers.append(t)
        
    def loop(self):
        while True:
            event = self.q.get()
            event.handle()

    def load_gatherers_list(self):
        class_list = []

        path = os.path.join(os.path.dirname(__file__), "gatherers")
        modules = pkgutil.iter_modules(path=[path])

        for _, module_name, _ in modules:
            module = __import__(path + '.' + module_name, fromlist=['*'])
            for name in dir(module):
                o = getattr(module, name)
                if inspect.isclass(o) and issubclass(o, gatherers.gatherer.Gatherer) and o is not gatherers.gatherer.Gatherer:
                    class_list.append(o)
        return class_list


if __name__ == "__main__":
    g = GatherAgent()
    g.start()
