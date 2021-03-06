# Generated by Django 3.2.9 on 2021-11-08 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BranchInformationM',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Company_Name', models.CharField(blank=True, max_length=255, null=True)),
                ('Branch_Name', models.CharField(blank=True, max_length=255, null=True)),
                ('Address', models.TextField(blank=True, max_length=500, null=True)),
                ('Short_Name', models.CharField(blank=True, max_length=50, null=True)),
                ('Phone', models.CharField(blank=True, max_length=50, null=True)),
                ('Fax', models.CharField(blank=True, max_length=50, null=True)),
                ('Email', models.EmailField(blank=True, max_length=50, null=True)),
                ('Branch_Code', models.CharField(blank=True, max_length=100, null=True)),
                ('BranchLogo', models.ImageField(blank=True, null=True, upload_to='logo')),
            ],
        ),
    ]
