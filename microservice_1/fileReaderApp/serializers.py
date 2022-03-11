from fileReaderApp.models import PostCode
from rest_framework import serializers

class PostCodeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PostCode
        fields = "__all__"