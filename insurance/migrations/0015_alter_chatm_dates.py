# Generated by Django 3.2.9 on 2021-11-19 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0014_chatm_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatm',
            name='dates',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
