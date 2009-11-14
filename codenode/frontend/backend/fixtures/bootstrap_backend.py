#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file has been automatically generated, changes may be lost if you
# go and generate it again. It was generated with the following command:
# ./manage.py dumpscript backend

import datetime
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType

def run():
    from codenode.frontend.backend.models import BackendServer

    backend_backendserver_1 = BackendServer()
    backend_backendserver_1.name = u'local'
    backend_backendserver_1.address = u'http://localhost:8337'
    backend_backendserver_1.save()

    from codenode.frontend.backend.models import EngineType

    backend_enginetype_1 = EngineType()
    backend_enginetype_1.name = u'Python'
    backend_enginetype_1.backend = backend_backendserver_1
    backend_enginetype_1.description = None
    backend_enginetype_1.save()

    backend_enginetype_2 = EngineType()
    backend_enginetype_2.name = u'Example'
    backend_enginetype_2.backend = backend_backendserver_1
    backend_enginetype_2.description = None
    backend_enginetype_2.save()

    from codenode.frontend.backend.models import Python

    python = '/usr/bin/python'
    version = subprocess.Popen([python, '--version'], stderr=subprocess.PIPE).\
        stderr.read().split()[1].rstrip()
    backend_python_1 = Python()
    backend_python_1.executable = python
    backend_python_1.version = version
    backend_python_1.save()

    from codenode.frontend.backend.models import VirtualenvEngine

    backend_virtualenvengine_1 = VirtualenvEngine()
    backend_virtualenvengine_1.python = backend_python_1
    backend_virtualenvengine_1.name = u'Example'
    backend_virtualenvengine_1.freeze = u''
    backend_virtualenvengine_1.save()

    from codenode.frontend.backend.models import NotebookBackendRecord


