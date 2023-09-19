from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=500)
    username = models.CharField(unique=True, max_length=10)

    def __str__(self):
        return self.username


class AccountRecoveryOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=7)
    expires = models.DateTimeField()
