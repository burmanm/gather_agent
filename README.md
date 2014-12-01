## Basics

Small agent that collects basic system information and sends them to the RHQ Metrics. It is designed to avoid external dependencies and the only external dependency which it requires is the [rhq-metrics-python-client](https://github.com/burmanm/rhq-metrics-python-client)

## Creating your own collectors

Adding your own gatherers to the agent is simple, all you need to do is place a file in the gatherers directory which has a class that extends the Gatherer class. You only need to write your own gather(self) method, which returns an event (created using self.create_event) or a list of such events.

Example:
```python
from gatherer import Gatherer

class my_gatherer(Gatherer):

    def gather(self):
        return self.create_event(key, value)
```

If you need to pass configuration options to the gatherer while it's being loaded (which you can access with self.config['key']), add under the gather_agent.ini [Gatherer] section new properties with the format: classname.key=value (classname should be lowercased).

Example:
```
[Gatherers]
my_gatherer.example=value
```
