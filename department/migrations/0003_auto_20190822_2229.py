# Generated by Django 2.1.10 on 2019-08-22 22:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0002_auto_20190821_0906'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ('-created',)},
        ),
    ]
