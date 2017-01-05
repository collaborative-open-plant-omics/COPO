# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-05 12:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chunked_upload', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CopoChunkedUpload',
            fields=[
                ('chunkedupload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='chunked_upload.ChunkedUpload')),
            ],
            options={
                'abstract': False,
            },
            bases=('chunked_upload.chunkedupload',),
        ),
    ]
