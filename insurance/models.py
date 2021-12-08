from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class BranchInformationM(models.Model):
    id=models.AutoField(primary_key=True)
    Company_Name=models.CharField(max_length=255,null=True,blank=True)
    Branch_Name=models.CharField(max_length=255,null=True,blank=True)
    Address=models.TextField(max_length=500,null=True,blank=True)
    Short_Name=models.CharField(max_length=50,null=True,blank=True)
    Phone=models.CharField(max_length=50,null=True,blank=True)
    Fax=models.CharField(max_length=50,null=True,blank=True)
    Email=models.EmailField(max_length=50,null=True,blank=True)
    Branch_Code=models.CharField(max_length=100,null=True,blank=True)
    BranchLogo=models.ImageField(upload_to='logo',null=True,blank=True)
    objects=models.Manager()

    def logo(self):
        try:
            urls = self.BranchLogo.url
        except:
            urls = ''
        return urls
    def __str__(self):
        return self.Company_Name

class UserProfileM(models.Model):
    id=models.AutoField(primary_key=True)
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    Phone=models.CharField(max_length=100,null=True,blank=True)
    Present_Address=models.TextField(max_length=255,null=True,blank=True)
    Permanant_Address=models.TextField(max_length=255,null=True,blank=True)
    Image=models.ImageField(upload_to='User_image',null=True,blank=True)
    otp=models.CharField(max_length=6,null=True,blank=True)
    Email=models.CharField(max_length=30,null=True,blank=True)
    Branch_code=models.CharField(max_length=30,null=True,blank=True)
    objects=models.Manager()

    def uimages(self):
        try:
            urls=self.Image.url
        except:
            urls=''
        return urls




class chatM(models.Model):
    id=models.AutoField(primary_key=True)
    chat_box=models.CharField(max_length=1000,null=True,blank=True)
    mrno=models.CharField(max_length=50,null=True,blank=True)
    dates=models.DateTimeField(auto_now=True)
    users=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    branch=models.ForeignKey(UserProfileM,on_delete=models.CASCADE,null=True,blank=True)
    comment = models.CharField(max_length=1000, null=True, blank=True)
    objects = models.Manager()

    def __str__(self):
        return self.chat_box+" "+self.mrno+" "
