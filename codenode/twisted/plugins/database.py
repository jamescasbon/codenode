import os
import sys

from twisted.python import log

from codenode.backend.engine import EngineConfigurationBase
from codenode.frontend.backend.models import VirtualenvEngine


for ve in VirtualenvEngine.objects.all(): 
    
    if not ve.installed():
        print 'Creating VirtualenvEngine', ve.name
        ve.create()
    
    if not ve.is_up_to_date():
        print 'Configuring VirtualenvEngine', ve.name
        ve.configure()
    
    
    print 'Registering VirtualenvEngine', ve.name
    sys.modules[__name__].__dict__[ve.name] = ve.as_engine_configuration()