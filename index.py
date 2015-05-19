#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import importexport
import requests
import subprocess
from time import sleep
from sanji.core import Sanji
from sanji.core import Route
from sanji.connection.mqtt import Mqtt

from voluptuous import Schema
from voluptuous import Required
from voluptuous import REMOVE_EXTRA
from voluptuous import All
from voluptuous import Length

_logger = logging.getLogger("sanji.importexport")


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

    EXPORT_SCHEMA = Schema({
        Required("url"): All(str, Length(1, 4096)),
        "headers": {}
    }, extra=REMOVE_EXTRA)

    IMPORT_SCHEMA = Schema({
        Required("file"): EXPORT_SCHEMA
    }, extra=REMOVE_EXTRA)

    def init(self, *args, **kwargs):
        self.path_root = os.path.abspath(os.path.dirname(__file__))

    @Route(methods="post", resource="/system/export", schema=EXPORT_SCHEMA)
    def post(self, message, response):
        (output, filelist) = importexport.export_data()
        headers = message.data.get("headers", {})
        r = requests.post(
            message.data["url"],
            files={output: open(output, "rb")},
            headers=headers,
            verify=False)

        if r.status_code != requests.codes.ok:
            return response(
                code=r.status_code,
                data={"message": "Can't upload config."})

        resp = r.json()
        if "url" not in resp:
            return response(
                code=500, data={"message": "Can't get file link."})

        return response(data={"url": resp["url"]})

    @Route(methods="put", resource="/system/import", schema=IMPORT_SCHEMA)
    def put(self, message, response):
        import_file = "/tmp/import.tar.gz"
        headers = message.data["file"].get("headers", {})

        r = requests.get(
            message.data["file"]["url"],
            stream=True,
            headers=headers,
            verify=False)
        chunk_size = 1024

        if r.status_code != requests.codes.ok:
            return response(
                code=r.status_code,
                data={"message": "Can't download firmware."})

        with open(import_file, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

        try:
            importexport.import_data(
                path=os.getenv("IMPORT_PATH", '/'),
                input_file=import_file)
        except Exception, e:
            _logger.error(e, exc_info=True)
            return response(
                code=500, data={"message": "Import failed.", "log": e.message})

        response()
        sleep(3)
        subprocess.call("reboot")


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    _logger = logging.getLogger("sanji.importexport")

    import_export = Index(connection=Mqtt())
    import_export.start()
