import os

from codenode.backend.engine import EngineConfigurationBase

boot = """from codenode.engine.server import EngineRPCServer
from codenode.engine.picloud.interpreter import Interpreter
from codenode.engine.runtime import build_namespace
namespace = build_namespace
from codenode.engine import runtime
port = runtime.find_port()
server = EngineRPCServer(('localhost', port), Interpreter, namespace)
runtime.ready_notification(port)
server.serve_forever()
"""


class Picloud(EngineConfigurationBase):
    bin = 'python'
    args = ['-c', boot]
    env = os.environ
    path = os.path.expanduser('~')


picloud = Picloud()

