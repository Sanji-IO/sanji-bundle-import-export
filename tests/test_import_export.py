#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import shutil
import unittest
import logging

from sanji.connection.mockup import Mockup
from sanji.message import Message
from mock import patch
from mock import Mock

logger = logging.getLogger()

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
    from import_export import ImportExport
except ImportError as e:
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)

export_file = "/run/shm/export.tar"

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

    @patch("import_export.os.path.isfile")
    def test_get(self):
        # case 1: check code 200
        def resp(code=200, data=None):
            self.assertEqual(code, 200)
        self.ie.get(message=None, response=resp, test=True)
        self.assertTrue(os.path.isfile(export_file))
        '''
        # case 2: check code 400
        def resp(code=200, data=None):
            self.assertEqual(code, 400)
        with patch("os.path.isfile") as os_path_isfile:
            os_path_isfile.return_value = "False"
            self.ie.get(message=None, response=resp, test=True)
        '''
    def test_put(self):
        # case 1: message donsn't has data attribute


        # case 2: put success
        # case 2.1: ssh start success


        # case 2.2: ssh stop success


        # case 3: put failed
        # case 3.1: ssh start failed
        pass

    def test_collect_file(self):
        if not os.path.exists(self.file_folder):
            os.makedirs(self.file_folder)
            os.makedirs(self.file_folder + "/bundle_a/data")
            os.makedirs(self.file_folder + "/bundle_b/data")
            os.makedirs(self.file_folder + "/bundle_c/non_data")
        with open("/run/shm/test_import_export/bundle_a/data/a.json",
                  "w") as file:
            file.write("This is a file.")
        with open("/run/shm/test_import_export/bundle_b/data/b.json",
                  "w") as file:
            file.write("This is b file.")
        with open("/run/shm/test_import_export/bundle_c/non_data/non_c.json",
                  "w") as file:
            file.write("This is non_c file.")

        self.ie.collect_file("/run/shm/test_import_export", "data", ".json")
        self.assertEqual(self.ie.import_set,
                         set(["/run/shm/test_import_export/\
bundle_a/data/a.json",
                             "/run/shm/test_import_export/\
bundle_b/data/b.json"]))

    def test_tar_files(self):

        if not os.path.exists(self.file_folder):
            os.makedirs(self.file_folder)
        with open("/run/shm/test_import_export/a.txt", "w") as file:
            file.write("This is a file.")
        with open("/run/shm/test_import_export/b.txt", "w") as file:
            file.write("B B BBB")
        self.ie.import_set.add("/run/shm/test_import_export/a.txt")
        self.ie.import_set.add("/run/shm/test_import_export/b.txt")

        self.ie.export_folder = self.file_folder
        self.ie.export_file = self.file_name
        self.ie.tar_files()

        # case 1: check export.tar
        self.assertTrue(os.path.isfile(self.file_name))

if __name__ == "__main__":
    unittest.main()
