from django.db import models
from users.models import User

class MedicalRecord(models.Model):

    patient = models.ForeignKey(User, on_delete=models.CASCADE)

    diagnosis = models.TextField()
    treatment = models.TextField()
    observations = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
