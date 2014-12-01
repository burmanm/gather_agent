# Basics

## Introduction

This is a small system agent that collects basic system information and sends them to the RHQ Metrics. It is designed to avoid external dependencies and the only external dependency which it requires is the [rhq-metrics-python-client](https://github.com/burmanm/rhq-metrics-python-client)

The agent itself is nothing but a light layer between input channels (called gatherers) and output channel (called handlers).

## Configuration

The default configuration file is named gather_agent.ini and is divided to different sections. There are some basic configuration settings, which are not specific to any gatherers or handlers. The difference is that their key-name does not have dot (``.``) in them.

By default gather_agent sends events to the RHQ Metrics using rhq-metrics-python-client. To override this, change handler class in the General section. The server hostname and port are defined in the Handlers section with the properties names starting ``rhqmetricshandler.``

The collection interval is defined in the Gatherers section, under a properties name ``interval``. The value is defined in seconds and the default is 15 seconds.

## Running

To run your own instance of gather_agent, use the following syntax:

```
python gather_agent.py [ini-file]
```

If the ini-file is not defined, the default is to read from the gather_agent.ini. To stop the agent, simply kill it.

### Systemd

If you wish to automatically manage the gather_agent's lifecycle, one can run it as a systemd service. Create a file called 

1. Create /etc/systemd/system/gather-agent.service
```
[Unit]
Description=Small gather agent that sends system statistics to RHQ Metrics

[Service]
ExecStart=/usr/bin/python /path_to/gather_agent.py /path_to/config_file.ini
Restart=Always

[Install]
WantedBy=multi-user.target
```
2. Controlling systemd:
  1. To reload configuration file run ``sudo systemctl daemon-reload``
  2. To enable the service, run ``sudo systemctl enable gather-agent``
  3. To start the agent ``sudo systemctl start gather-agent``
  4. To stop the agent ``sudo systemctl stop gather-agent``

## Creating your own collectors

Adding your own gatherers to the agent is simple, all you need to do is place a file in the gatherers directory which has a class that extends the Gatherer class. You only need to write your own gather(self) method, which returns an event (created using self.create_event) or a list of such events.

Example:
```python
from gatherer import Gatherer

class my_gatherer(Gatherer):

    def gather(self):
        return self.create_event(key, value)
```

If you need to pass configuration options to the gatherer while it's being loaded add under the gather_agent.ini [Gatherer] section new properties with the format: classname.key=value (classname should be lowercased). To access them, fetch values with self.config['key']. If you need them on instance init, override init(self, config) function.

Example:
```
[Gatherers]
my_gatherer.example=value
```

```python

class my_gatherer(Gatherer):
    def init(self, config):
        self.example_property = config['example']
```

# Advanced

## Architecture

The agent uses a simple implementation of the reactor pattern (to demultiplex gatherers to a single stream of events towards the handler) where each gatherer is ran in their own thread. Whenever there's an event available, it sends that event to a blocking Queue, which is what the main thread is waiting to read. Once an event is sent to the queue, it is processed in the main thread by the handler. Thus, slow invocation of the handler will block processing of the next object.

The advantages is to keep the events serialized and to avoid any race conditions on the responding handler. To improve performance, the handler could use some sort of buffering to prevent spamming the receiving end. This is however the job of the handler and the actual dispatcher will always send events if there's any waiting in the queue.
