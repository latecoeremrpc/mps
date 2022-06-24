from django.test import SimpleTestCase
from django.urls import resolve, reverse
from app.views import result,shopfloor,save_coois,save_zpp

class TestUrls(SimpleTestCase):
    
    def test_result_url(self):
        url = reverse('result')
        self.assertEquals(resolve(url).func, result)
        
    def test_smoothing_url(self):
        url = reverse('shopfloor')
        self.assertEquals(resolve(url).func,shopfloor)    
        
    def test_coois_url(self):
        url = reverse('savecoois')
        self.assertEquals(resolve(url).func,save_coois)  
    
    
    def test_zpp_url(self):
        url = reverse('savezpp')
        self.assertEquals(resolve(url).func,save_zpp)             

