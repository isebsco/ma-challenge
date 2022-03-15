import requests
import time

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from django.shortcuts import render
from django.http import HttpResponse

from rest_framework            import generics, status
from rest_framework.response   import Response

        
class ConsumePostCodesApiView(generics.ListAPIView):
    """
    A view that receives coordinates consumes https://api.postcodes.io/ API
    and return the JSON received. It must be a 200 response from external API, 
    otherwise, it trys one more time or until receive the data
    """
    def get(self,*args,**kwargs):
        lat=self.kwargs['lat']
        lon=self.kwargs['lon']
        #url to get the post codes data
        url_api= "http://api.postcodes.io/postcodes?lon="+lon+"&lat="+lat
        #pull data from third party rest api
        response = requests.get(url_api)
        while response.json()['status'] != 200:
            time.sleep(0.5) 
            response = requests.get(url_api)
        #convert reponse data into json and send as response
        return Response(response.json(),status=status.HTTP_200_OK) 