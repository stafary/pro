from django.db import models

# Create your models here.
class picture(models.Model):
    username = models.CharField(max_length=100)
    image = models.ImageField(upload_to = 'pic_folder/', default = 'pic_folder/None/no-img.jpg')
    place = models.CharField(max_length=100)
    comment = models.CharField(max_length=200)
    name = models.CharField(max_length =100) 
    def __unicode__(self):
        return (u"%s %s %s %s" %(self.username,self.place,self.comment,self.name)).decode("utf-8")