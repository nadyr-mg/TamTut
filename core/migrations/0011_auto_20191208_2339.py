# Generated by Django 2.2.7 on 2019-12-08 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20191208_2249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hobby',
            name='user',
        ),
        migrations.AddField(
            model_name='profile',
            name='hobby',
            field=models.ManyToManyField(to='core.Hobby'),
        ),
    ]
