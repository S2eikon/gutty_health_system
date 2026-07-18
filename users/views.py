from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Nuevos imports para la API REST de perfil
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserProfileSerializer


# REGISTRO

def register_view(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            role = request.POST.get('role')

            if role in ['patient', 'doctor']:
                user.role = role
            else:
                user.role = 'patient'

            user.save()
            login(request, user)

            return redirect('/appointments/')

    return render(request, 'users/register.html', {'form': form})


# LOGIN

def login_view(request):
    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('/appointments/')

    return render(request, 'users/login.html', {'form': form})


# LOGOUT

def logout_view(request):
    logout(request)
    return redirect('/users/login/')


# =========================
# PERFIL DE USUARIO (API)
# =========================

class ProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
