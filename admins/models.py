from django.db import models

# Create your models here.
class qappx(models.Model):
    id=models.IntegerField(primary_key=True,)
    cpu=models.IntegerField(null=True)
    mem=models.IntegerField(null=True)
    a=models.IntegerField(null=True)
    Q=models.FloatField(null=True)
