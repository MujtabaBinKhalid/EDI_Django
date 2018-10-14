from django.db import models


class EDIAccount(models.Model):

    ipHost = models.CharField(max_length=250)
    userName = models.CharField(max_length=500)
    password = models.CharField(max_length=100)
    # email = models.CharField(max_length=500,  default='emailAddress')
    input_path = models.CharField(max_length=1000)
    output_path = models.CharField(max_length=1000)
    ip_hostOut = models.CharField(max_length=250)
    user_nameOut = models.CharField(max_length=1000)
    passwordOut = models.CharField(max_length=1000)

    def __str__(self):
        return self.userName + " - " + self.ipHost
