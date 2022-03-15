import csv
import requests
import aiohttp
import asyncio
import time

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from rest_framework import viewsets, generics, status, views
from rest_framework.decorators import action
from rest_framework.response import Response

from fileReaderApp.models import PostCode
from fileReaderApp.serializers import PostCodeSerializer

fs = FileSystemStorage(location='tmp/')


class PostCodeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for saving and updating PostCode.
    """
    queryset = PostCode.objects.all()
    serializer_class = PostCodeSerializer

    # decorator to add action and extra route to upload the file
    @action(detail=False, methods=['POST'])
    def upload_file(self, request):
        """
        Method to upload data from CSV, it will receive the file, store it in the temp folder.
        
        Then this method will open the document within a generator to start reading row by row,
        after that it will create in bulk the postcodes elements in the DB.
        
        Finally, it will bulk_update the created elements consuming the 2 microservices which connects
        with the external API.
        """
        start1 = time.time()
        file = request.FILES["file"]
        content = file.read()
        file_content = ContentFile(content)
        file_name = fs.save("_tmp.csv", file_content)
        tmp_file = fs.path(file_name)
        
        def rows_generator(file_name, skip_first_line=True, dialect='excel', **fmtparams):
            with open(file_name, 'r') as csv_file:
                reader = csv.reader(csv_file, dialect, **fmtparams)
                if skip_first_line:
                    next(reader, None)#avoid first row
                for row in reader:
                    yield row

        post_codes_list = []#List to the bulk create
        errors_counter = 0 #flag to count errors in the csv file
        total_coords=0
        
        for row in rows_generator(tmp_file, skip_first_line=True):
            total_coords+=1
            if len(row)!=2 or row[0]=='0' or row[1]=='0':
                errors_counter += 1
            else:
                (lat, lon) = row
                post_codes_list.append(PostCode(lat=lat, lon=lon))

        PostCode.objects.bulk_create(post_codes_list)
        
        list_size=len(post_codes_list)
        end1 = time.time()
        print("reading the file and saving data postcodes takes "+ str(end1-start1))
        start2 = time.time()
        saved_post_codes=(list(PostCode.objects.all().order_by('-id')))[:list_size]
        print("loading postcodes takes "+ str(time.time()-start2))
        start3 = time.time()
        async def main():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for postcode in saved_post_codes:
                    task = asyncio.ensure_future(get_postcode_data(session, postcode))
                    tasks.append(task)
                counter = await asyncio.gather(*tasks)
                
        async def get_postcode_data(session, pc):
            lat1=pc.lat
            lon1=pc.lon            
            url = f'http://127.0.0.1:7000/consumeapi/{lat1}/{lon1}'

            async with session.get(url) as response:
                result_data = await response.json()
                if result_data['result'] is not None:
                    pc.data=result_data['result'][0]
                else:
                    pc.data={"without data"}

        asyncio.run(main()) 
                  
        PostCode.objects.bulk_update(saved_post_codes,['data'] )
        print("Time consumin exteral API "+ str(time.time()-start3))

        return Response("Successfully upload the data. " + str(total_coords) + " rows processed, " + str(errors_counter) + " rows with errors in the csv file")


class PostCodesUpdateView(generics.ListAPIView):
    """
    A view that updates the jsonField taking into account the data received
    """
    serializer_class = PostCodeSerializer

    def get(self, request, *args, **kwargs):
        data1 = request.data
        querySet = PostCode.objects.filter(
            lat=self.kwargs['lat']).filter(lon=self.kwargs['lon'])
        post_code = PostCode.objects.get(
            lat=self.kwargs['lat'], lon=self.kwargs['lon'])
        if querySet.exists():
            post_code.data = data1
            post_code.save()
            return Response("PostCode Info Updated", status=status.HTTP_200_OK)
        else:
            return Response("Post Code doesn't exist", status=status.HTTP_404_NOT_FOUND)
