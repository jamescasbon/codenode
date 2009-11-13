from django.test import TestCase

import models as m

class TestBackendModels(TestCase):
    
    def test_create_VirtualenvEngine(self):
        
        ve = m.VirtualenvEngine(name='unit_test')
        
        ve.save()
        
        1/0