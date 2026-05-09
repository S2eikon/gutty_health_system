from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment
from django.contrib.auth.decorators import login_required


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    appointment.status = 'cancelled'
    appointment.save()

    return redirect('appointments_list')


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        appointment.date = request.POST['date']
        appointment.time = request.POST['time']
        appointment.status = 'rescheduled'
        appointment.save()

        return redirect('appointments_list')

    return render(request, 'appointments/reschedule.html', {
        'appointment': appointment
    })