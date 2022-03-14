from django.db import models
from django.conf import settings

import collections
import jsonfield

class PostCode(models.Model):
    id   = models.AutoField(primary_key=True)
    lat  = models.CharField(max_length=50)
    lon  = models.CharField(max_length=50)
    data = jsonfield.JSONField(blank=True, null=True, load_kwargs={'object_pairs_hook': collections.OrderedDict})
    
    def __str__(self):
        return "Lat is " + self.lat +" and lon is " + self.lon