#!/usr/bin/env python

from distutils.core import setup

setup(name='gather-agent',
      version='0.4.1',
      description='Simple agent that gathers basic system statistics to RHQ Metrics',
      author='Michael Burman'
      author_email='miburman@redhat.com',
      url='http://github.com/burmanm/gather_agent',
      packages='gather_agent'
      )
