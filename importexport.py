#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import fnmatch
import glob
import tarfile
import datetime
import logging
import requests


_logger = logging.getLogger("sanji.importexport")
_SANJI_BUNDLE_PREFIX = "/usr/lib/sanji-1.0/"
_WEBAPP_FILE_LIST = ["/var/www/webapp/server/webapp.db",
                     "/var/www/webapp/public/assets/images/users"]
IMPORT_PATH = "/"


class ImportError(Exception):
    pass


def get_bundle_data_filelist(bundles_root):
    """
    Get given bundles_root filelist
    """
    matches = [
        os.path.join(root, filename)
        for root, dirnames, filenames in os.walk(bundles_root)
        for filename in fnmatch.filter(filenames, "*")
    ]

    return [f for f in matches if
            f.find(".factory") == -1 and
            f.find(".backup") == -1]


def get_all_bundles(bundles_home):
    """
    Get all bundles use glob */data
    """
    return glob.glob(os.path.join(bundles_home, "*/data"))


def tar_files(filelist, output):
    """
    Tar and Compress (gz) to output directory
    """
    with tarfile.open(output, "w:gz") as tar:
        for name in filelist:
            if not os.path.exists(name):
                continue
            _logger.debug("Packing %s" % (name))
            tar.add(name)

    return output


def export_data(
    output="/run/shm/export-%s.tar.gz" %
    (datetime.datetime.now().strftime("%Y%m%d%H%M")),
    bundles_home=None,
    extra_files=None
):
    """
    Collect all BUNDLES_HOME/{bundles}/data/* exclude *.factory, *.backup.
    Web database should be included.
    Args:
        output: defaults to /run/shm/export-{timestamp}.tar.gz
        bunldes_home: Bundles home
        extra_files(None): If not assign, defaults to _WEBAPP_FILE_LIST
    Returns:
        (output path, filelist)
    """
    if bundles_home is None:
        bundles_home = os.getenv("BUNDLES_HOME", "/usr/lib/sanji-1.0")

    if extra_files is None:
        extra_files = _WEBAPP_FILE_LIST

    collectedFiles = [
        files
        for bundle in get_all_bundles(bundles_home)
        for files in get_bundle_data_filelist(bundle)
    ] + extra_files

    tar_files(collectedFiles, output)

    return (output, collectedFiles)


def import_data(path="/", input_file="", bundle_names=[], delete=True):
    """
    Import configs to path /
    """
    filelist = []
    try:
        with tarfile.open(input_file, "r:gz") as tar:
            members = [tarinfo for tarinfo in tar
                       if filename_filter(tarinfo.name, bundle_names)]
            if len(tar.getmembers()) != len(members):
                _logger.info("Some import files have been omitted.")
            tar.extractall(path, members)
            filelist = [m.name for m in members]
    except Exception as e:
        _logger.error(str(e))

    if delete:
        try:
            os.unlink(input_file)
            _logger.debug("Clean up temp file: %s" % input_file)
        except Exception as e:
            _logger.warning("Can't delete: %s" % input_file)

    return filelist


def filename_filter(filename, bundle_names=[]):
    """Filter for filenames, only accepts:
        _SANJI_BUNDLE_PREFIX and _WEBAPP_FILE_LIST
        Returns:
            True: Accept
            False: Reject
    """
    filename = "/%s" % filename

    def _filename_filter():
        for fn in _WEBAPP_FILE_LIST:
            if filename.find(fn) != -1:
                return True

        if len(bundle_names) == 0:
            if filename.startswith(_SANJI_BUNDLE_PREFIX):
                return True
            else:
                return False

        for bundle_name in bundle_names:
            if filename.startswith(_SANJI_BUNDLE_PREFIX + bundle_name):
                return True

        return False

    if _filename_filter() is False:
        _logger.debug("Ignore: %s" % (filename))
        return False

    _logger.info("Import: %s" % (filename))
    return True


class HTTPError(Exception):
    pass


def import_from_http(
        url, headers={}, bundle_names=[], tmpfile="/tmp/upgrade.download"):
    r = requests.get(
        url=url,
        stream=True,
        headers=headers,
        verify=False
    )
    chunk_size = 1024
    if r.status_code != requests.codes.ok:
        raise HTTPError("Can't download file.")

    with open(tmpfile, 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)

    return import_data(
        path="/", input_file=tmpfile, bundle_names=bundle_names)


def export_to_http(url, headers={}):
    (output, filelist) = export_data()
    r = requests.post(
        url=url,
        files={output: open(output, "rb")},
        headers=headers,
        verify=False
    )

    if r.status_code != requests.codes.ok:
        _logger.debug("Response code: %s" % str(r.status_code))
        raise HTTPError("Can't upload files.")

    resp = r.json()
    if "url" not in resp:
        _logger.debug("Resp: %s" % str(resp))
        raise HTTPError("Can't get file link.")

    return resp["url"]
