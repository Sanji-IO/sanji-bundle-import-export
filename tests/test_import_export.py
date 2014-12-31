#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import unittest
import logging

from sanji.connection.mockup import Mockup
from sanji.message import Message
from mock import patch

logger = logging.getLogger()

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
    from import_export import ImportExport
except ImportError as e:
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)


class TestSshClass(unittest.TestCase):

    def setUp(self):
        self.import_export = ImportExport(connection=Mockup())

    def tearDown(self):
        self.import_export = None

    def test_init(self):

        # case 1: ssh start failed

        # case 2: ssh start success


    def test_get(self):
        # case 1: check code


        # case 2: check data of enable = 1


        # case 3: check data of enable = 0


    def test_put(self):
        # case 1: message donsn't has data attribute


        # case 2: put success
        # case 2.1: ssh start success


        # case 2.2: ssh stop success


        # case 3: put failed
        # case 3.1: ssh start failed


if __name__ == "__main__":
    unittest.main()
