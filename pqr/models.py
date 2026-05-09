from django.db import models
from users.models import User

class PQR(models.Model):

    TYPE_CHOICES = [
        ('complaint', 'Queja'),
        ('claim', 'Reclamo'),
        ('suggestion', 'Sugerencia'),
        ('praise', 'Felicitación'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    pqr_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)