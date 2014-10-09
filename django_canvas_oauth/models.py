from django.db import models
from django.contrib.auth.models import User


class OAuthToken(models.Model):
    token = models.CharField(max_length=128) #oauth_middleware token has length 64
    user = models.OneToOneField(User)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
