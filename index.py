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


def download(url, output):
    r = requests.get(url, stream=True)
    chunk_size = 1024

    if r.status_code != requests.codes.ok:
        return False

    with open(output, 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)

    return True


class Index(Sanji):
    def init(self, *args, **kwargs):
        self.path_root = os.path.abspath(os.path.dirname(__file__))

    @Route(methods="post", resource="/system/export")
    def post(self, message, response):
        headers = message.data.get("headers", {})
        (output, filelist) = importexport.export_data()
        r = requests.post(
            message.data["url"],
            files={output: open(output, "rb")},
            headers=headers,
            verify=False)

        if r.status_code != requests.codes.ok:
            return response(code=500, data={"message": "Can't upload config."})

        resp = r.json()
        if "url" not in resp:
            return response(
                code=500, data={"message": "Can't get file link."})

        return response(data={"url": resp["url"]})

    @Route(methods="put", resource="/system/import")
    def put(self, message, response):
        import_file = "/tmp/import"
        headers = message.data.get("headers", {})

        r = requests.get(
            message.data["file"]["url"],
            stream=True,
            headers=headers,
            verify=False)
        chunk_size = 1024

        if r.status_code != requests.codes.ok:
            return response(data={message: "Can't download firmware."})

        with open(import_file, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

        importexport.import_data(path="/run/shm", input_file=import_file)
        return response({})


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("importexport")

    import_export = Index(connection=Mqtt())
    import_export.start()
