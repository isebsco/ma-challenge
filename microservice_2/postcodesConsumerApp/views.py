import requests

from django.shortcuts import render
from django.http import HttpResponse

from rest_framework            import generics, status
from rest_framework.response   import Response

        
class ConsumePostCodesApiView(generics.ListAPIView):
    """
    A view that consume de https://api.postcodes.io/ API
    """
    def get(self,*args,**kwargs):
        lat=self.kwargs['lat']
        lon=self.kwargs['lon']
        #url to verify if the codes exists
        url_ms1= "http://127.0.0.1:8000/postcodes/"
        #url to get the post codes data
        url_api= "http://api.postcodes.io/postcodes?lon="+lon+"&lat="+lat
        #pull data from third party rest api
        response = requests.get(url_api)
        #convert reponse data into json
        return Response(response.json(),status=status.HTTP_200_OK)