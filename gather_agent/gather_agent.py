import Queue
import handlers
import inspect
import threading
import pkgutil
import os
import sys
import imp
from gatherer import Gatherer
import signal
import platform
import ConfigParser

class GatherAgent(object):

    KEY_SEPARATOR = '.'
    
    def start(self, config_file='gather_agent.ini'):
        self.q = Queue.Queue()
        self.gatherers = []

        # Load configuration properties
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        config.set('Gatherers', 'prefix', platform.node())
        self.config = config

        # Start gatherers and handlers..
        self.handler = self.start_handler(config.get('General', 'handler'))
        self.start_gatherers(self.load_gatherers(), self.handler)

        signal.signal(signal.SIGINT, self._stop)
        self.active = True        
        
        self.loop()

    def start_handler(self, handler_cls):
        handler_generic_config = self.load_partial_config('Handlers')
        handler_specific_config = self.load_partial_config('Handlers', handler_cls)
        handler_specific_config.update(handler_generic_config)

        for o in self.load_classes_list('handlers'):
            if o.__name__ == handler_cls:
                obj = o(handler_specific_config)
                return obj

    def start_gatherers(self, instances, handler):
        for instance in instances:
            t = threading.Thread(target=instance.run)
            t.daemon = True
            t.start()
            self.gatherers.append(instance)
        
    def loop(self):
        while self.active:
            event = self.q.get()
            event.handle()

    def load_partial_config(self, section, keyprefix=None):
        section_config = self.config.items(section)
        partial_config = {}
        for k, v in section_config:
            d = None            
            if keyprefix is not None:
                keyprefix = keyprefix.lower()
                i = k.rfind(keyprefix + self.KEY_SEPARATOR)
                if i > -1:                    
                    d = { k: v }
            else:
                i = k.rfind(self.KEY_SEPARATOR)
                if i < 0:
                    d = { k: v }
            if d is not None:
                partial_config.update(d)
        return partial_config

    def load_handlers_config(self, class_name):
        handlers_config = self.load_partial_config('Handlers', class_name)
        return handlers_config
    
    def load_gatherers_config(self, class_name):
        #general_config = self.load_partial_config('General')
        generic_gatherer_config = self.load_partial_config('Gatherers')
        specific_gatherer_config = self.load_partial_config('Gatherers', class_name)
        generic_gatherer_config.update(specific_gatherer_config)
        return generic_gatherer_config

    def load_classes_list(self, package):
        path = os.path.join(os.path.dirname(__file__), package)
        modules = pkgutil.iter_modules(path=[path])

        for _, module_name, _ in modules:
            fp, pathname, description = imp.find_module(module_name, [path])
            module = imp.load_module(module_name, fp, pathname, description)
            
            for name in dir(module):
                o = getattr(module, name)
                if inspect.isclass(o):
                    yield o
    
    def load_gatherers(self):
        instances = []

        path = os.path.join(os.path.dirname(__file__), "gatherers")
        modules = pkgutil.iter_modules(path=[path])

        for _, module_name, _ in modules:
            fp, pathname, description = imp.find_module(module_name, [path])
            module = imp.load_module(module_name, fp, pathname, description)
            
            for name in dir(module):
                o = getattr(module, name)
                if inspect.isclass(o) and issubclass(o, Gatherer) and o is not Gatherer:
                    partial_config = self.load_gatherers_config(name)
                    obj = o(self.handler, partial_config, self.q)
                    instances.append(obj)
        return instances

    def _stop(self, signum, frame):
        print 'Received signal ' + str(signum) + ', closing gatherers and handlers'
        self.active = False
        for i in self.gatherers:
            i.close()
        self.handler.close()

if __name__ == "__main__":
    g = GatherAgent()
    if len(sys.argv) > 1:
        g.start(sys.argv[1])
    g.start()
