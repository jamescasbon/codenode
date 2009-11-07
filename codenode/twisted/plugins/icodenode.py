import os

from codenode.backend.engine import EngineConfigurationBase

# this is the path that needs to be available to import frontend.settings that is needed 
# for django database connections
installed_path = (os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

boot = """
import sys
sys.path.insert(0, "%s")
from codenode.engine.server import EngineRPCServer
from codenode.engine.interpreter import Interpreter
from codenode.engine import runtime
namespace = runtime.build_namespace
port = runtime.find_port()
server = EngineRPCServer(('localhost', port), Interpreter, namespace)
runtime.ready_notification(port)
server.serve_forever()
""" % installed_path

class Icodenode(EngineConfigurationBase):
    bin = 'python'
    args = ['-c', boot]
    env = os.environ
    path = os.path.expanduser('~')


icodenode = Icodenode()