#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import requests
import subprocess
import json
from time import sleep
from sanji.core import Sanji
from sanji.core import Route
from sanji.connection.mqtt import Mqtt

from voluptuous import Schema
from voluptuous import Required
from voluptuous import REMOVE_EXTRA
from voluptuous import All
from voluptuous import Length

from importexport import import_from_http
from importexport import export_to_http
from importexport import HTTPError

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
        "headers": dict
    }, extra=REMOVE_EXTRA)

    IMPORT_SCHEMA = Schema({
        Required("file"): EXPORT_SCHEMA,
        "scopes": list
    }, extra=REMOVE_EXTRA)

    def init(self, *args, **kwargs):
        self.path_root = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(self.path_root, "config", "scopes.json")) as f:
            self.scopes_dict = json.load(f)

    @Route(methods="post", resource="/system/export", schema=EXPORT_SCHEMA)
    def post(self, message, response):
        headers = message.data.get("headers", {})
        try:
            url = export_to_http(
                url=message.data["url"],
                headers=headers)
            return response(data={"url": url})
        except HTTPError as he:
            _logger.error("Export to http error: %s" % str(he))
            return response(code=500, data={"message": str(he)})
        except Exception as e:
            _logger.error("Export to http error")
            _logger.error(str(e))
            raise e

    @Route(methods="put", resource="/system/import", schema=IMPORT_SCHEMA)
    def put(self, message, response):
        headers = message.data["file"].get("headers", {})
        scopes = message.data.get("scopes", None)
        if scopes is None:
            return response(code=400, data={"message": "scopes is required."})

        bundle_names = []
        for scope in scopes:
            if scope not in self.scopes_dict:
                continue
            bundle_names = bundle_names + self.scopes_dict[scope]

        _logger.info("Import bundles: %s" % ", ".join(bundle_names))
        try:
            import_from_http(
                url=message.data["file"]["url"],
                headers=headers,
                bundle_names=bundle_names)
            _logger.info("Imported. Ready to reboot...")
        except HTTPError as he:
            _logger.error("Import from http error: %s" % str(he))
            return response(code=500, data={"message": str(he)})
        except Exception as e:
            _logger.error("Import from http error")
            _logger.error(str(e))
            return response(code=500, data={"message": "Import failed."})

        response()
        sleep(3)
        subprocess.call("reboot")


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    _logger = logging.getLogger("sanji.importexport")

    import_export = Index(connection=Mqtt())
    import_export.start()
