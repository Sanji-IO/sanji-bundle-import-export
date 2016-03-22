#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import shutil
import unittest
import logging

from sanji.connection.mockup import Mockup
# from sanji.message import Message
# from mock import patch
# from mock import Mock

logger = logging.getLogger()

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
    from importexport import ImportExport
except ImportError as e:
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)


class TestImportExportClass(unittest.TestCase):
    file_folder = "/run/shm/test_import_export"
    file_name = "/run/shm/test_import_export/export.tar"

    def setUp(self):
        if os.path.isfile(self.file_name) is True:
            os.remove(self.file_name)
        self.ie = ImportExport(connection=Mockup())

    def tearDown(self):
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
        if os.path.isdir(self.file_folder):
            shutil.rmtree(self.file_folder)

        self.ie = None

    def test_init(self):
        self.assertEquals(self.ie.model.model_name, "import_export")

if __name__ == "__main__":
    unittest.main()
