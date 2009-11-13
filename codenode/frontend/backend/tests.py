import os
import subprocess
import shutil

from django.test import TestCase

import models as m

class TestBackendModels(TestCase):
        
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
        
        assert not ve.installed()
        ve.create()
        assert ve.installed()
        
        