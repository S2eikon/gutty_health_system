from django.db import models
from users.models import User

class Payment(models.Model):

    patient = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)