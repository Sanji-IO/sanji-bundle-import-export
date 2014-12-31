#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import subprocess
import tarfile
import time
import threading
from sanji.core import Sanji
from sanji.core import Route
from sanji.model_initiator import ModelInitiator
from sanji.connection.mqtt import Mqtt

logger = logging.getLogger()


class ImportExport(Sanji):
    def init(self, *args, **kwargs):
        self.import_set = set()
        self.path_root = os.path.abspath(os.path.dirname(__file__))
        self.export_folder = "/run/shm"
        self.export_file = self.export_folder + "/export.tar"
        self.search_root = "/home/bundle"
        self.db_postfix = ".json"
        self.db_folder_name = "data"
        self.model = ModelInitiator("import_export", self.path_root)

    @Route(methods="get", resource="/system/importexport")
    def get(self, message, response):
        # export_config
        self.collect_file(self.search_root, self.db_postfix,
                          self.db_folder_name)
        #self.exclude_file()
        if os.path.isfile(self.export_file):
            return response(code=200, data="/system/importexport/download")
        else:
            return response(code=400, data={"message": "Invaild Input"})

    @Route(methods="put", resource="/system/importexport")
    def put(self, message, response):
        if self.restore_file() is True:
            return response(code=200, data="/system/importexport/download")
        else:
            return response(code=400, data={"message": "Invaild Input"})

        # reboot system to apply new configuration files.
        thread_id = threading.Thread(target=self.reboot_thread)
        thread_id.daemon = True
        thread_id.start()

    def restore_file(self):
        if os.path.isfile(self.export_file) is True:
            # TODO:
            #   Kill all model here.
            tar = tarfile.open(self.export_file)
            tar.extractall("/")
            tar.close()
            return True
        else:
            return False

    def collect_file(self, start_root, dir_keyword,
                     postfix, unique=False):
        # search
        for root, dirs, files in os.walk(start_root):
            for dir in dirs:
                for file in files:
                    #print root, dir, file
                    if file.endswith(postfix) and dir == dir_keyword:
                        source_file = os.path.join(root, file)
                        #tar.add(os.path.abspath(source_file))
                        self.import_set.add(os.path.abspath(source_file))
                        if unique is True:
                            break

    '''
    def exclude_file(self, keyword):
        for item in self.import_set:
            if item.split("/")[-1] == keyword:
                self.exclude_set.add(item)

        print self.exclude_set

        self.import_set = self.import_set.difference(self.exclude_set)
        print self.import_set
    '''

    def tar_files(self):
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)

        if os.path.exists(self.export_file):
            os.remove(self.export_file)

        tar = tarfile.open(self.export_file, "a")
        for file in self.import_set:
            tar.add(file)
        tar.close()

    def reboot_thread(self):
        time.sleep(5)   # Wait 5 seconds. Web need to transfer to main page.
        cmd = 'reboot'
        subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("importexport")

    import_export = ImportExport(connection=Mqtt())
    import_export.start()
