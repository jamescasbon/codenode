import os

from codenode.backend.engine import EngineConfigurationBase

boot = """from codenode.engine.server import EngineRPCServer
from codenode.engine.v8 import Interpreter
from codenode.engine import runtime
port = runtime.find_port()
server = EngineRPCServer(('localhost', port), Interpreter, None)
runtime.ready_notification(port)
server.serve_forever()
"""

class V8(EngineConfigurationBase):
    bin = 'python'
    args = ['-c', boot]
    env = os.environ
    path = os.path.expanduser('~')

V8 = V8()

