import csv

from django.core.files.base    import ContentFile
from django.core.files.storage import FileSystemStorage
from rest_framework            import viewsets, generics, status, views
from rest_framework.decorators import action
from rest_framework.response   import Response

from fileReaderApp.models import PostCode
from fileReaderApp.serializers import PostCodeSerializer

fs = FileSystemStorage(location='tmp/')

class PostCodeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing PostCode.
    """
    queryset = PostCode.objects.all()
    serializer_class = PostCodeSerializer

    #decorator to add action and extra route to upload the file
    @action(detail=False, methods=['POST'])
    def upload_file(self, request):
        """
        Method to upload data from CSV
        """
        file = request.FILES["file"]

        content = file.read()  
        file_content = ContentFile(content)
        file_name = fs.save(
            "_tmp.csv", file_content
        )
        tmp_file = fs.path(file_name)

        csv_file = open(tmp_file, errors="ignore")
        reader = csv.reader(csv_file)
        next(reader)
        
        post_codes_list = []
        for id_, row in enumerate(reader):
            (lat,lon) = row
            post_codes_list.append(
                PostCode(
                    lat=lat,
                    lon=lon
                )
            )

        PostCode.objects.bulk_create(post_codes_list)

        return Response("Successfully upload the data")

class PostCodesListAll (generics.ListAPIView):
    serializer_class = PostCodeSerializer
    def get_queryset(self):
        querySet = PostCode.objects.all()
        return querySet

class PostCodesUpdateView(generics.ListAPIView):
    """
    A view that updates the jsonField taking into account the data received
    """
    serializer_class = PostCodeSerializer    
    def get(self,request,*args,**kwargs):
        data1 = request.data
        querySet = PostCode.objects.filter(lat=self.kwargs['lat']).filter(lon=self.kwargs['lon'])
        post_code = PostCode.objects.get(lat=self.kwargs['lat'], lon=self.kwargs['lon'])
        if querySet.exists():
            post_code.data = data1
            post_code.save()
            return Response("PostCode Info Updated",status=status.HTTP_200_OK)
        else:
            return Response("Post Code doesn't exist",status=status.HTTP_404_NOT_FOUND)
