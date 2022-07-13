# Generated by Django 4.0.6 on 2022-07-13 11:13

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_squashed_0006_alter_availableheight_height'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedimage',
            name='height',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='uploadedimage',
            name='image',
            field=models.ImageField(height_field='height', upload_to=api.models.UploadedImage.upload_to),
        ),
    ]