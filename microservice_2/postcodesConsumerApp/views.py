from django.shortcuts import render
from django.http import HttpResponse
import requests
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
        url_ms1= "http://127.0.0.1:7000/postcodes/"
        #url to get the post codes data
        url_api= "http://api.postcodes.io/postcodes?lon="+lon+"&lat="+lat
        #pull data from third party rest api
        response = requests.get(url_ms1)
        #convert reponse data into json
        print(url_ms1)
        print(response.json()[0])
        return Response("Pos tCode info received",status=status.HTTP_200_OK)
        