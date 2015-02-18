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
    """
    A simple layer between inputs (gatherers) and output (handler) using a simple
    implementation of reactor pattern.
    """

    KEY_SEPARATOR = '.'
    
    def start(self, config_file='gather_agent.ini'):
        """
        Initialization method of the GatherAgent. Sets up required queues, arses 
        the configuration, loads gatherers and handler and starts the dispatcher.
        """
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

        for o, _ in self.load_classes_list('handlers'):
            if o.__name__ == handler_cls:
                obj = o(handler_specific_config)
                return obj

    def start_gatherers(self, instances, handler):
        """
        Creates new threads for each gatherer running the gatherer's run() method
        """
        for instance in instances:
            t = threading.Thread(target=instance.run)
            t.daemon = True
            t.start()
            self.gatherers.append(instance)
        
    def loop(self):
        """
        Main dispatcher loop which waits for available objects in the queue. Once
        an event is received, it calls event's handler and waits for results before
        processing the next event.
        """
        while self.active:
            event = self.q.get()
            event.handle()

    def load_partial_config(self, section, keyprefix=None):
        """
        Parses a partial configuration from the ini-file, filtering any key that
        isn't defined by the keyprefix. If no keyprefix is given, filters all the
        properties that are namespaced with dot (.)
        """
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
        generic_gatherer_config = self.load_partial_config('Gatherers')
        specific_gatherer_config = self.load_partial_config('Gatherers', class_name)
        generic_gatherer_config.update(specific_gatherer_config)
        return generic_gatherer_config

    def load_classes_list(self, package):
        """
        Loads all classes from the given package. Returns a generator with two
        parameters, class_name and the module
        """
        path = os.path.join(os.path.dirname(__file__), package)
        modules = pkgutil.iter_modules(path=[path])

        for _, module_name, _ in modules:
            fp, pathname, description = imp.find_module(module_name, [path])
            module = imp.load_module(module_name, fp, pathname, description)
            
            for name in dir(module):
                o = getattr(module, name)
                if inspect.isclass(o):
                    yield o, name

    def load_gatherers(self):
        """
        Creates and returns a generator with one instance of each gatherers
        object.
        """
        for o, name in self.load_classes_list('gatherers'):
            if issubclass(o, Gatherer) and o is not Gatherer:
                partial_config = self.load_gatherers_config(name)
                obj = o(self.handler, partial_config, self.q)
                yield obj

    def _stop(self, signum, frame):
        """
        If a signal is received from the OS, this method is used to clean up and
        stop all the gatherers and handlers.
        """
        print 'Received signal ' + str(signum) + ', closing gatherers and handlers'
        self.active = False
        for i in self.gatherers:
            i.close()
        self.handler.close()

if __name__ == "__main__":
    g = GatherAgent()
    if len(sys.argv) > 1:
        g.start(sys.argv[1])
    else:
        g.start()
