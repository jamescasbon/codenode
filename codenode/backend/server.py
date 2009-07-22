
from twisted.python import log
from twisted.python import usage
from twisted.internet import defer
from twisted.internet import reactor
from twisted.application import service
from twisted.application import internet
from twisted.web import xmlrpc
from twisted.web import resource
from twisted.web import server

from zope.interface import Interface, implements

from codenode.backend import core

BACKEND_VERSION = '0.2'

class BackendAdmin(resource.Resource):
    
    def __init__(self, backend):
        resource.Resource.__init__(self)
        self.backend = backend

        self.putChild("RPC2", BackendAdminRC(backend))
        self.putChild("", self)

    def render(self, request):
        """
        """
        return 'backend admin'

class BackendAdminRC(xmlrpc.XMLRPC):

    def __init__(self, backend):
        xmlrpc.XMLRPC.__init__(self)
        self.backend = backend

    def xmlrpc_listEngineTypes(self):
        return self.backend.getEngineTypes()

    def xmlrpc_listEngineInstances(self):
        return self.backend.listEngineInstances()

    @defer.inlineCallbacks
    def xmlrpc_runEngineInstance(self, engine_type):
        d = self.backend.newEngine(engine_type)
        res = yield d
        print 'rpc newengine', res
        defer.returnValue(res)

    def xmlrpc_terminateEngineInstance(self, engine_id):
        self.backend.terminateEngineInstance(engine_id)

    def xmlrpc_interruptEngineInstance(self, engine_id):
        self.backend.interruptEngineIntance(engine_id)
        return


class BackendClient(resource.Resource):

    def __init__(self, backend):
        resource.Resource.__init__(self)
        self.backend = backend

        #self.putChild("RPC2", BackendClientRC(backend))
        self.putChild("", self)

    def getChild(self, path, request):
        return BackendClientRC(self.backend, path)

    def render(self, request):
        return "backend client"

class BackendClientRC(xmlrpc.XMLRPC):

    def __init__(self, backend, id):
        xmlrpc.XMLRPC.__init__(self)
        self.backend = backend
        engine = backend.client_manager.getEngine(id)
        self.engine = engine

    def xmlrpc_evaluate(self, to_evaluate):
        return self.engine.evaluate(to_evaluate)

    def xmlrpc_complete(self, to_complete):
        return self.engine.complete(to_complete)

class BackendRoot(resource.Resource):

    def __init__(self, backend):
        resource.Resource.__init__(self)
        self.backend = backend

        self.putChild("admin", BackendAdmin(backend))
        self.putChild("client", BackendClient(backend))
        self.putChild("", self)

    def render(self, request):
        return 'backend root'


class BackendConfig(usage.Options):

    optParameters = [
            ['host', 'h', settings.BACKEND_HOST, 'Interface to listen on'],
            ['port', 'p', settings.BACKEND_PORT, 'Port number to listen on', int],
            ['env_path', 'e', os.path.join(os.getenv('HOME'), '.codenode', 'kernel'), 
                'Path containing config, tac, and db'],
            ]

    def opt_version(self):
        print 'codenode backend version: %s' % BACKEND_VERSION
        sys.exit(0)

class BackendServerServiceMaker(object):

    impleents(service.IServiceMaker, service.IPlugin)
    tapname = "codenode-backend"
    description = ""
    options = BackendConfig

    def makeServices(self, options):

        backendServices = service.MultiService()
        client_manager = core.EngineProxyManager() #sessions
        client_manager.setServiceParent(backendServices)
        proc_manager = core.EngineManager()
        proc_manager.setServiceParent(backendServices)

        backend = core.Backend(proc_manager, client_manager)

        eng_proxy_factory = server.Site(BackendRoot(backend))
        internet.TCPServer(options['port'], eng_proxy_factory,
                interface=options['host']).setServiceParent(backendServices)
        return backendServices


