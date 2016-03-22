#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import fnmatch
import glob
import tarfile
import datetime
import logging

_logger = logging.getLogger("sanji.importexport")


def get_bundle_data_filelist(bundle_root):
    """
    Get given bundles filelist
    """
    matches = []
    for root, dirnames, filenames in os.walk(bundle_root):
        for filename in fnmatch.filter(filenames, '*'):
            matches.append(os.path.join(root, filename))

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


def export_data(output="/run/shm/export-%s.tar.gz" %
                (datetime.datetime.now().strftime("%Y%m%d%H%M"))):
    """
    Collect all BUNDLES_HOME/{bundles}/data/* exclude *.factory, *.backup.
    Web database should be included.
    return (output path, filelist)
    """
    bundles_home = os.getenv("BUNDLES_HOME", "/usr/lib/sanji-1.0")
    collectedFiles = []
    for bundle_data_path in get_all_bundles(bundles_home):
        collectedFiles += get_bundle_data_filelist(bundle_data_path)

    # FIXME: use configuration file to include extra backup files
    collectedFiles.append("/var/www/webapp/server/webapp.db")
    collectedFiles.append("/var/www/webapp/public/assets/images/users")

    return (output, tar_files(collectedFiles, output))


def import_data(path="/", input_file=""):
    """
    Import configs to path /
    """
    filelist = []
    with tarfile.open(input_file, "r:gz") as tar:
        tar.extractall(path)
        members = tar.getmembers()
        for m in members:
            _logger.debug("Unpacking %s" % (m.name))
            filelist.append(m.name)

    return filelist
