import csv
import requests

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
    A ViewSet for viewing and editing PostCode.
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
        file = request.FILES["file"]

        content = file.read()
        file_content = ContentFile(content)
        file_name = fs.save("_tmp.csv", file_content)
        tmp_file = fs.path(file_name)
        
        def rows_generator(file_name, skip_first_line=True, dialect='excel', **fmtparams):
            with open(file_name, 'r') as csv_file:
                reader = csv.reader(csv_file, dialect, **fmtparams)
                if skip_first_line:
                    next(reader, None)
                for row in reader:
                    yield row

        #csv_file = open(tmp_file, errors="ignore")
        #reader = csv.reader(csv_file)
        #next(reader)#avoid first row

        post_codes_list = []#List to the bulk create
        errors_counter = 0 #flag to count errors in the csv file
        coords_without_data=0
        total_coords=0
        url_ms2= "http://127.0.0.1:7000/consumeapi/"
        for row in rows_generator(tmp_file, skip_first_line=True):
            total_coords+=1
            if len(row)!=2 or row[0]=='0' or row[1]=='0':
                errors_counter += 1
            else:
                (lat, lon) = row
                post_codes_list.append(PostCode(lat=lat, lon=lon))

        PostCode.objects.bulk_create(post_codes_list)
        
        saved_post_codes=list(PostCode.objects.all())        
        for postcode in saved_post_codes:
            lat1=postcode.lat
            lon1=postcode.lon
            response = requests.get(url_ms2 + lat1 + "/" + lon1)            
            if response.json()['result'] is not None:
                postcode.data=response.json()['result'][0]
            else:
                postcode.data={"without data"}
                coords_without_data+=1
            

        PostCode.objects.bulk_update(saved_post_codes,['data'] )


        return Response("Successfully upload the data. " + str(total_coords) + " rows processed, " + str(errors_counter) + " rows with errors in the csv file and " + str(coords_without_data) + " coords without related data")

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
