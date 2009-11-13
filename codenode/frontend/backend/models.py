import os 
import subprocess
import tempfile 

from django.db import models
from django.contrib.auth.models import User

from codenode.frontend.notebook.models import Notebook

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
    """A python installation. Must have virtualenv installed. """
    executable = models.CharField(max_length=255)
    version = models.CharField(max_length=10)
        
class VirtualenvEngine(models.Model):
    """A managed python engine in a virtualenv.
    
    Note we don't store the location of the files or executables here as they could be different 
    on a backend server.  Instead they are calculated from the current settings.
    """
    python = models.ForeignKey(Python)
    name = models.CharField(max_length=100, primary_key=True)
    
    @property
    def directory(self):
        return os.path.join(VE_PATH, self.name)
    
    @property 
    def executable(self):
        return os.path.join(self.directory, 'bin', 'python')
        
    @property
    def site_packages(self):
        # must be a better way from using site to return the correct directory 
        return os.path.join(self.directory, 'lib', 'python' + self.python.version[:3], 'site-packages')
    
    def installed(self):
        return os.path.exists(self.directory) and os.path.exists(self.executable)
    
    virtualenv_incantation = "import sys,pkg_resources; sys.exit( \
        pkg_resources.load_entry_point('virtualenv', 'console_scripts', 'virtualenv')())"
    
    codenode_code = os.path.abspath(os.path.join(os.path.basename(__file__), '..','..','..'))
    
    def __unicode__(self):
        return u"Virtualenv Engine %s" % (self.name,)
    
    def create(self):

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
        # TODO: check for errors in the output 

        # Link in the codenode code.       
        os.symlink(self.codenode_code, os.path.join(self.site_packages, 'codenode'))

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


