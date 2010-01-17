######################################################################### 
# Copyright (C) 2007, 2008, 2009 
# Alex Clemesha <alex@clemesha.org> & Dorian Raymer <deldotdr@gmail.com>
# 
# This module is part of codenode, and is distributed under the terms 
# of the BSD License:  http://www.opensource.org/licenses/bsd-license.php
#########################################################################

import os
import shutil
import sys
import inspect
from functools import wraps

from django.core.management import call_command
from django.core.management.base import CommandError

import codenode
from codenode import management


def setup_django(command):
    """ This decorator wraps an admin command to provide django setup.
    
    For standard development settings, use -devel flag. 
    For desktop settings use -desktop.
    For a django app, use '-settings mysite.settings'.
    Otherwise, pick up the settings from the cwd
    """
    @wraps(command)
    def wrapper(devel=False, desktop=False, settings=False, *args, **kwargs):
        
        if 'DJANGO_SETTINGS_MODULE' not in os.environ:
            if devel: 
                os.environ['DJANGO_SETTINGS_MODULE'] = 'codenode.frontend._devel_settings'
                check_home_dir()
                
            elif desktop:
                os.environ['DJANGO_SETTINGS_MODULE'] = 'codenode.frontend._desktop_settings'
                check_home_dir()

            elif settings: 
                os.environ['DJANGO_SETTINGS_MODULE'] = settings

            else:
                if not os.path.exists(os.path.join('frontend', 'settings.py')):
                    print 'frontend.settings does not exists, please use inside a directory created with codenode-admin init'
                    sys.exit(1)
                sys.path = [os.getcwd()] + sys.path
                os.environ['DJANGO_SETTINGS_MODULE'] = 'frontend.settings'
        
        # use devel_mode if we are running the devel env
        if devel and 'devel_mode' in inspect.getargspec(command)[0]:
            kwargs['devel_mode'] = True

        return command(*args, **kwargs)

    return wrapper
    
    
def build_twisted_cli(command, daemonize=False, devel_mode=False):
    """
    Build twisted incantation for a particular command
    """
    from django.conf import settings
    
    cmd = "twistd "
    if not daemonize:
        cmd += "-n "
    cmd += "%s " % command
    cmd += "--env_path=%s " % settings.HOME_PATH
    
    if command != 'codenode-backend':
        cmd += "--server_log=%s " % os.path.join(settings.HOME_PATH, 'server.log')
        cmd += "--static_files=%s " % settings.MEDIA_ROOT
        
    if devel_mode: 
        cmd += "--devel_mode " 
    return cmd
    
    
def check_home_dir():
    """
    Check an environment directory contains a database and search index, etc. and required directories.
    """
    # non top level imports to prevent django settings setup before we have handled it
    from django.conf import settings
    from codenode.frontend.backend.fixtures.development import run as bootstrap_database
    from codenode.frontend.search import search
    
    for required_directory in [
            settings.HOME_PATH,
            settings.PLOT_IMAGES
        ]:
        if not os.path.exists(required_directory):
            os.mkdir(required_directory)
        
    if not os.path.exists(settings.DATABASE_NAME):
        call_command('syncdb', interactive=False)
        bootstrap_database()
        
    # a check for database schema version should go in here
    
    search.create_index()


def init_command(name=None, test=False):
    """
    Initialize a codenode.

    Creates a new directory that will contain all needed
    sub-directories, config files, and other data to run
    an instance of codenode.
    
    Use the test flag to create a development environment
    where the code is symlinked.
    
    EXAMPLES:
        codenode-admin init -name mycodenode
        
        codenode-admin init -name mycodenode -test
    """
    
    osjoin = os.path.join
    abspath = os.path.abspath(".")
    envroot = osjoin(abspath, name)
    pkgroot = os.sep.join(codenode.__file__.split(os.sep)[:-1])
    os.mkdir(envroot)
    
    copytree = shutil.copytree
    
    if test:
        try: 
            copytree = os.symlink
        except AttributeError:
            pass   

    for dir in ["frontend", "backend"]:
        os.makedirs(osjoin(envroot, dir))
        open(osjoin(osjoin(envroot, dir), "__init__.py"), "w").close()
        settingsfile = osjoin(osjoin(pkgroot, dir), "_settings.py")
        shutil.copyfile(settingsfile,  osjoin(osjoin(envroot, dir), "settings.py"))

    for dir in ["static", "templates"]:
        dirroot = osjoin("frontend", dir)
        pkgdirroot = osjoin(pkgroot, dirroot)
        copytree(pkgdirroot, osjoin(envroot, dirroot))

    pkgdataroot = osjoin(pkgroot, "data")
    copytree(pkgdataroot, osjoin(envroot, "data"))

    pkgtwistedroot = osjoin(pkgroot, "twisted")
    copytree(pkgtwistedroot, osjoin(envroot, "twisted"))


@setup_django
def run_command(daemonize=False): #, frontendpid=None):
    """
    Run local desktop version of Codenode.  
    Use inside a directory created with "codenode-admin init".

    """
    os.system(build_twisted_cli('codenode', daemonize))


@setup_django
def frontend_command(daemonize=False, devel_mode=False):
    """
    Run the Frontend server.
    """
    os.system(build_twisted_cli('codenode-frontend', daemonize, devel_mode))


@setup_django
def backend_command(daemonize=False, devel_mode=False):
    """
    Run a Backend Server.
    """
    os.system(build_twisted_cli('codenode-backend', daemonize, devel_mode))


@setup_django
def syncdb_command():
    """
    Run Django's `syncdb`.
    """
    call_comand('syncdb', interactive=False)


@setup_django
def bootstrapdb_command():
    """
    Load default codenode setup: an admin user, and a local backend with a python engine.
    """
    from codenode.frontend.backend.fixtures.development import run as bootstrap_database
    bootstrap_database()


@setup_django
def dbshell_command():
    """
    Database shell
    """
    call_command('dbshell')


@setup_django
def shell_command():
    """
    Open a python shell.
    """
    try:
        call_command('shell_plus')
    except CommandError:
        call_command('shell')
        
@setup_django
def resetdb_command():
    """
    Open a database shell.
    """
    call_command('reset_db')
    call_command('syncdb', interactive=False)
    from codenode.frontend.backend.fixtures.development import run as bootstrap_database
    bootstrap_database()
        

def backendmanhole_command():
    """
    Open a manhole to the backend.
    """
    # TODO: pick up port from configuration
    os.system('telnet localhost 6024')


def frontendmanhole_command():
    """ 
    Open a manhole to the frontend.
    """
    # TODO: pick up port from configuration
    os.system('telnet localhost 6023')
    
        
def help_command(**options):
    """
    Prints out help for the commands. 

    codenode-admin help

    You can get help for one command with:

    codenode-admin help -for start
    """
    if "for" in options:
        help = management.args.help_for_command(management.codenode_admin, options['for'])
        if help:
            print help
        else:
            management.args.invalid_command_message(management.codenode_admin, exit_on_error=True)
    else:
        print "codenode-admin help:\n"
        print "\n".join(management.args.available_help(management.codenode_admin))

