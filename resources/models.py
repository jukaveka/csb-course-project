from django.db import models
from django.contrib.auth.models import User

class Resource(models.Model):
  name = models.CharField(max_length=40)
  url = models.URLField()
  file_path = models.CharField()
  notes = models.CharField(max_length=1000)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  is_active = models.BooleanField(default=True)