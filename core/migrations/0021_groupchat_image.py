# Generated by Django 2.2.7 on 2020-01-14 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20200108_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupchat',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='profile_pics'),
        ),
    ]
