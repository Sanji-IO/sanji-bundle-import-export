#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import subprocess
import time
import threading
import importexport
import requests
import json

from sanji.core import Sanji
from sanji.core import Route
from sanji.connection.mqtt import Mqtt

logger = logging.getLogger()


class Index(Sanji):
    def init(self, *args, **kwargs):
        self.path_root = os.path.abspath(os.path.dirname(__file__))

    @Route(methods="post", resource="/system/export")
    def post(self, message, response):
        (output, filelist) = importexport.export_data()
        r = requests.post(
            message.data["url"],
            files={output: open(output, "rb")},
            verify=False)
        resp = r.json()

        response(data={"url": resp["url"]})

    # @Route(methods="put", resource="/system/import")
    # def put(self, message, response):
    #     # reboot system to apply new configuration files.
    #     thread_id = threading.Thread(target=self.reboot_thread)
    #     thread_id.daemon = True
    #     thread_id.start()

    # def reboot_thread(self):
    #     time.sleep(5)   # Wait 5 seconds. Web need to transfer to main page.
    #     cmd = 'reboot'
    #     subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("importexport")

    import_export = Index(connection=Mqtt())
    import_export.start()
