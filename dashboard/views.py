from django.shortcuts import render
from appointments.models import Appointment
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):

    total = Appointment.objects.count()
    pending = Appointment.objects.filter(status='pending').count()
    confirmed = Appointment.objects.filter(status='confirmed').count()
    cancelled = Appointment.objects.filter(status='cancelled').count()

    context = {
        'total': total,
        'pending': pending,
        'confirmed': confirmed,
        'cancelled': cancelled
    }

    return render(request, 'dashboard/dashboard.html', context)