# Generated by Django 2.2.7 on 2019-12-26 11:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20191226_1400'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfeed',
            name='title',
        ),
    ]
