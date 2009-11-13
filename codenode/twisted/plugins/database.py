import os
import sys

from twisted.python import log

from codenode.backend.engine import EngineConfigurationBase
from codenode.frontend.backend.models import VirtualenvEngine


for ve in VirtualenvEngine.objects.all(): 
    sys.modules[__name__].__dict__[ve.name] = ve.as_engine_configuration()