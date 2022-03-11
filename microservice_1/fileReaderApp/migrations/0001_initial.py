# Generated by Django 3.2.7 on 2022-03-11 21:34

import collections
from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PostCode',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('lat', models.CharField(max_length=50)),
                ('lon', models.CharField(max_length=50)),
                ('data', jsonfield.fields.JSONField(blank=True, load_kwargs={'object_pairs_hook': collections.OrderedDict}, null=True)),
            ],
        ),
    ]