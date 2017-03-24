#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import unittest
import logging
import requests

from mock import patch
from mock import ANY
from mock import mock_open
from mock import Mock

logger = logging.getLogger()

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
    from importexport import get_bundle_data_filelist, get_all_bundles, \
        export_data, filename_filter,\
        import_from_http, export_to_http
    import importexport
except ImportError as e:
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)


class TestImportExportFunctions(unittest.TestCase):
    def setUp(self):
        self.bundles_home = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "mock_bundles_root"
        )
        importexport.IMPORT_PATH = "/tmp/import"

    def tearDown(self):
        pass

    def test_get_bundle_data_filelist(self):
        filelist = get_bundle_data_filelist(
            os.path.join(self.bundles_home, "mock_bundle_1", "data")
        )
        self.assertEqual(len(filelist), 1)

    def test_get_all_bundles(self):
        """Get all bundle paths"""
        bundle_paths = get_all_bundles(self.bundles_home)
        self.assertEqual(len(bundle_paths), 2)

    @patch("importexport.tar_files")
    def test_export_data(self, tar_files):
        output, filelist = export_data(
            output="/tmp/temp.tar.gz",
            bundles_home=self.bundles_home,
            extra_files=[]
        )
        self.assertEqual(output, "/tmp/temp.tar.gz")
        self.assertEqual(len(filelist), 2)
        tar_files.assert_called_once_with([ANY, ANY], ANY)
        for filename in filelist:
            self.assertTrue(filename.endswith(".json"))

    def test_import_data(self):
        pass

    def test_filename_filter(self):
        self.assertFalse(filename_filter("/home/moxa", "modubs"))
        self.assertFalse(filename_filter(
            "/usr/lib/sanji-1.0/modbus/data/data.json", "modbus"))

    @patch("requests.get")
    @patch("importexport.import_data")
    def test_import_from_http(self, import_data, mock_get):
        mock_resp_get = Mock()
        mock_resp_get.status_code = requests.codes.ok
        mock_resp_get.iter_content = Mock(return_value=iter([]))
        mock_get.return_value = mock_resp_get

        m = mock_open()
        with patch("__builtin__.open", m, create=True):
            import_from_http(url=None)
            m.assert_called_with(ANY, "wb")

    @patch("requests.post")
    @patch("importexport.export_data")
    def test_export_to_http(self, export_data, mock_post):
        mock_resp_post = Mock()
        mock_resp_post.status_code = requests.codes.ok
        mock_resp_post.json.return_value = {"url": "testurl"}
        mock_post.return_value = mock_resp_post

        export_data.return_value = "", []
        m = mock_open()
        with patch("__builtin__.open", m, create=True):
            export_to_http(url=None, headers={})
            m.assert_called_with(ANY, "rb")


if __name__ == "__main__":
    unittest.main()
