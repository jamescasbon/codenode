import os
import sys

from twisted.python import log

from codenode.backend.engine import EngineConfigurationBase
from codenode.frontend.backend.models import EngineType

from python import boot as standard_python_boot


class DatabaseEngineConfiguration(EngineConfigurationBase):
    """ Subclass to avoid use of class name for registered name """

    def __init__(self, name):
        self.name = name


for enginetype in EngineType.objects.all(): 
    
    if enginetype.name.startswith('ve'):
    
        engine = DatabaseEngineConfiguration(enginetype.name)
        engine.args = ['-c', standard_python_boot]
        engine.env = os.environ
        
        # obviously we need a better database model of virtualenv based environments
        engine.bin = os.path.join(enginetype.description, 'bin', 'python')
        
        # twisted plugin does a lookup on the module __dict__ to get plugins 
        sys.modules[__name__].__dict__[enginetype.name] = engine