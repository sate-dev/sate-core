#! /usr/bin/env python

import unittest
import datetime
import logging
import os
import shutil, glob

from sate.test import get_testing_configuration, data_source_path, TestLevel, is_test_enabled
from sate import get_logger, log_exception
from sate.alignment import Alignment, MultiLocusDataset
from sate.scheduler import jobq, start_worker
from sate.filemgr import TempFS
from sate.usersettingclasses import StringUserSetting, IntUserSetting

_LOG = get_logger(__name__)

config = get_testing_configuration()
start_worker(1)

class TreeEstimatorTest(unittest.TestCase):
    def setUp(self):
        self.ts = TempFS()
        self.ts.create_top_level_temp(prefix='treeEstimatorTest', parent=os.curdir)
        self.filename = data_source_path('mafft.anolis.fasta')
        self.alignment = Alignment()
        self.alignment.read_filepath(data_source_path('mafft.anolis.fasta'),
                'FASTA')

    def tearDown(self):
        dir_list = self.ts.get_remaining_directories()
        for dir in dir_list:
            try:
                self.ts.remove_dir(dir)
            except ValueError:
                pass

    def get_tree_estimator(self, name):
        try:
            return config.create_tree_estimator(name=name, temp_fs=self.ts)
        except RuntimeError:
            log_exception(_LOG)
            _LOG.warn("""Could not create an aligner of type %s !

This could indicate a bug in create_tree_estimator_using_config() or could mean that
your installation is not configured to run this tool.
""" % name)
            return None

    def _impl_test_tree_estimator(self, name, datatype, partitions, **kwargs):
        num_cpus = kwargs.get('num_cpus', None)
        filename = data_source_path('anolis.fasta')

        md = MultiLocusDataset()
        md.read_files(seq_filename_list=[filename],
                datatype=datatype)
        md.relabel_for_sate()
        # alignment = Alignment()
        # alignment.read_filepath(filename, 'FASTA')
        te = self.get_tree_estimator(name)
        if te is None:
            _LOG.warn("test%s skipped" % name)
            return
        # alignment.datatype = datatype
        if num_cpus:
            a = te.run(alignment=md,
                       partitions=partitions,
                       tmp_dir_par=self.ts.top_level_temp,
                       delete_temps=True,
                       num_cpus=num_cpus)
        else:
            a = te.run(alignment=md,
                       partitions=partitions,
                       tmp_dir_par=self.ts.top_level_temp,
                       delete_temps=True)

    def testRaxml(self):
        # if is_test_enabled(TestLevel.SLOW, _LOG):
        self._impl_test_tree_estimator('raxml', datatype="DNA",
                partitions=[("DNA", 1, 1456)])

    def testFastTree(self):
        config.fasttree.add_option('options', StringUserSetting(
                name='options',
                default='', 
                short_name=None,
                help='Options to be passed to FastTree.',
                subcategory=None))
        self._impl_test_tree_estimator('fasttree', datatype="DNA",
                partitions=[("DNA", 1, 1456)])

    def testFastTreeMP(self):
        config.fasttree.add_option('options', StringUserSetting(
                name='options',
                default='',
                short_name=None,
                help='Options to be passed to FastTree.',
                subcategory=None))
        self._impl_test_tree_estimator('fasttree', datatype="DNA",
                partitions=[("DNA", 1, 1456)], num_cpus=2)

if __name__ == "__main__":
    unittest.main()
