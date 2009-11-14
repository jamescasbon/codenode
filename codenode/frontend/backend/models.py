import os 
import subprocess

from django.db import models
from django.contrib.auth.models import User

from codenode.backend.engine import EngineConfigurationBase
from codenode.frontend.notebook.models import Notebook

python_engine_incantation = """from codenode.engine.server import EngineRPCServer
from codenode.engine.interpreter import Interpreter
from codenode.engine import runtime
namespace = runtime.build_namespace
port = runtime.find_port()
server = EngineRPCServer(('localhost', port), Interpreter, namespace)
runtime.ready_notification(port)
server.serve_forever()
"""

# this should be imported from settings, but that isn't avaliable until a codenode is actually created
VE_PATH = '/tmp'


class BackendServer(models.Model):
    """This currently assumes the server is accessed via http (xmlrpc) by
    the way the address is stored.
    """
    name = models.CharField(max_length=100)
    # put validation check in to make sure address is good
    address = models.CharField("Server address (e.g. http://localhost:9000)", max_length=100)

    def __unicode__(self):
        return u"Backend Server %s @ %s" % (self.name, self.address)

class EngineType(models.Model):
    """Establish (un)official set of attributes.
    These attributes are defined in the backend plugin.
    """
    name = models.CharField(max_length=100)
    backend = models.ForeignKey(BackendServer)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u"%s Engine Type " % (self.name,)
        
class Python(models.Model):
    """A python installation. Must have virtualenv and pip installed. """
    executable = models.CharField(max_length=255)
    version = models.CharField(max_length=10)
    
    # TODO: offer a check method for virtualenv and pip
    def __unicode__(self):
        return u"Notebook Engine Type: %s" % (self.engine_type,)
        
class VirtualenvEngine(models.Model):
    """A managed python engine in a virtualenv.
    
    Note we don't store the location of the files or executables here as they could be different 
    on a backend server.  Instead they are calculated from the current settings.
    """
    python = models.ForeignKey(Python)
    name = models.CharField(max_length=100, primary_key=True)
    freeze = models.TextField(blank=True)
    
    @property
    def directory(self):
        return os.path.join(VE_PATH, self.name)
    
    @property 
    def executable(self):
        return os.path.join(self.directory, 'bin', 'python')
    
    @property 
    def pip(self):
        return os.path.join(self.directory, 'bin', 'pip')    
    
    @property
    def site_packages(self):
        # must be a better way from using site module to return the correct directory 
        return os.path.join(self.directory, 'lib', 'python' + self.python.version[:3], 'site-packages')
    
    def installed(self):
        return os.path.exists(self.directory) and os.path.exists(self.executable)
    
    virtualenv_incantation = "import sys,pkg_resources; sys.exit( \
        pkg_resources.load_entry_point('virtualenv', 'console_scripts', 'virtualenv')())"
        
    codenode_code = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
    
    def __unicode__(self):
        return u"Virtualenv Engine %s" % (self.name,)
    
    def create(self):
        """ create the environment and install the codenode engine code """
        # Create the virtualenv.
        # You cannot access the virtualenv API directly unless running from a 'real' python
        # so invoke the script instead
        subprocess.check_call(
            [self.python.executable, 
                '-c', self.virtualenv_incantation, 
                '--no-site-packages', self.directory], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        # Link in the codenode code.
        os.symlink(self.codenode_code, os.path.join(self.site_packages, 'codenode'))
    
    def configure(self):
        """ configure the virtualenv by installing the required packages """
        package_list  = self.freeze.split()
        
        # TODO - this should return its output so that the user can see what happens when something
        # goes wrong
        subprocess.check_call(
            [self.pip, 'install'] + package_list,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
    
    def as_engine_configuration(self):
        """ return an engine configuration """
        engine = EngineConfigurationBase(self.name)
        engine.args = ['-c', python_engine_incantation]
        engine.env = os.environ
        engine.bin = self.executable
        return engine

class NotebookBackendRecord(models.Model):
    """
    Each notebook gets an engine access id from the backend server.
    The access id is a token for making computation requests to the
    backend. The backend associates the access id with an engine type.
    """
    notebook = models.ForeignKey(Notebook, unique=True, related_name='backend')
    engine_type = models.ForeignKey(EngineType)
    access_id = models.CharField(max_length=32)

    def __unicode__(self):
        return u"Notebook Engine Type: %s" % (self.engine_type,)


