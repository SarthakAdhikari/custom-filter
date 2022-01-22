from django.db import models


class Travel(models.Model):
    date = models.DateField()
    distance = models.IntegerField()
