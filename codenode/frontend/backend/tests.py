import os
import subprocess
import shutil

from django.test import TestCase

import models as m

# fixtures contains a minimal package to install
test_freeze = os.path.join(os.path.dirname(__file__), 'fixtures', 'dummy-1.tar.gz')

class TestBackendModels(TestCase):
    
    # mark the test as slow so you can exclude it with ./test.sh -a \!slow
    slow = True
    
    def setUp(self):
        if os.path.exists('/tmp/unit_test'):
            shutil.rmtree('/tmp/unit_test')
            
            
    def _check_installed(self, python, package):
        try:
            subprocess.check_call([python ,'-c', "import %s" % package], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            raise Exception('package %s not available in %s' % (package, python)) 
    
    def test_create_VirtualenvEngine(self):
        
        # get the system python version so that this can work on other peoples machines
        version = subprocess.Popen(['/usr/bin/python', '--version'], stderr=subprocess.PIPE).\
            stderr.read().split()[1].rstrip()
            
        py = m.Python(version=version, executable='/usr/bin/python')
        py.save()
        
        ve = m.VirtualenvEngine(python=py, name='unit_test', freeze=test_freeze)
        ve.save()
        
        # try creating it 
        assert not ve.installed()
        ve.create()
        assert ve.installed()
        
        # try get is as engine configuration
        assert ve.as_engine_configuration()
        
        # if it was created correctly we should be able to import codenode to create the engine
        self._check_installed(ve.executable, 'codenode')
        
        # now run the configure and test the imports
        ve.configure()
        self._check_installed(ve.executable, 'dummy')

        