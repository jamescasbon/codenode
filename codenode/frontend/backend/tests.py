import os
import subprocess
import shutil

from django.test import TestCase

import models as m

class TestBackendModels(TestCase):
    
    # mark the test as slow so you can exclude it with ./test.sh -a \!slow
    slow = True
    
    def setUp(self):
        if os.path.exists('/tmp/unit_test'):
            shutil.rmtree('/tmp/unit_test')
        
    def tearDown(self):
        if os.path.exists('/tmp/unit_test'):
            shutil.rmtree('/tmp/unit_test')
    
    def test_create_VirtualenvEngine(self):
        
        # get the system python version so that this can work on other peoples machines
        version = subprocess.Popen(['/usr/bin/python', '--version'], stderr=subprocess.PIPE).\
            stderr.read().split()[1].rstrip()
            
        py = m.Python(version=version, executable='/usr/bin/python')
        py.save()
        
        ve = m.VirtualenvEngine(python=py, name='unit_test')
        ve.save()
        
        # try creating it 
        assert not ve.installed()
        ve.create()
        assert ve.installed()
        
        # get is as engine configuration
        assert ve.as_engine_configuration()
        
        