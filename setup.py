#!/usr/bin/env python2.7

from distutils.core import setup

setup(name         = 'broom',
      version      = 'ALPHA',
      description  = 'Broom',
      package_dir  = {'': 'lib'},
      packages     = [
          'broom',
          'broom.client',
          'broom.ext',
          'broom.ext.google',
          'broom.graph',
          'broom.source',
          'broom.utility',
          'cmdb',
          ],
      author       = 'Syntropy Corporation',
      author_email = 'info@syntropyco.com',
      url          = 'http://syntropco.com/'
      )
