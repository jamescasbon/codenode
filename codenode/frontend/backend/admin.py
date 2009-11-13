from django.contrib import admin

from codenode.frontend.backend.models import BackendServer
from codenode.frontend.backend.models import EngineType
from codenode.frontend.backend.models import NotebookBackendRecord
from codenode.frontend.backend.models import Python
from codenode.frontend.backend.models import VirtualenvEngine

from codenode.frontend.backend import rpc

class BackendServerAdmin(admin.ModelAdmin):
    """
    """

    def save_model(self, request, obj, form, change):
        if not change:
            engine_types = rpc.listEngineTypes(obj.address)
            obj.save()
            for e_type in engine_types:
                engine_type = EngineType(name=e_type, backend=obj)
                engine_type.save()

admin.site.register(BackendServer, BackendServerAdmin)

class EngineTypeAdmin(admin.ModelAdmin):
    """
    """

admin.site.register(EngineType, EngineTypeAdmin)


class NotebookBackendRecordAdmin(admin.ModelAdmin):
    """
    """

admin.site.register(NotebookBackendRecord, NotebookBackendRecordAdmin)


class PythonAdmin(admin.ModelAdmin):
    """
    """

admin.site.register(Python, PythonAdmin)


class VirtualenvEngineAdmin(admin.ModelAdmin):
    """
    """
    def save_model(self, request, obj, form, change):
        obj.save()
        obj.create()
    
admin.site.register(VirtualenvEngine, VirtualenvEngineAdmin)