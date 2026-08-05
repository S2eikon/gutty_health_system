from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django import forms

from .models import User

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)

from .serializers import (
    UserProfileSerializer,
    UserSerializer
)

from audit.services import create_audit


# ======================================================
# FORMULARIO DE REGISTRO
# ======================================================

class RegisterForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput
    )

    class Meta:

        model = User

        fields = [
            "username",
            "password1",
            "password2",
        ]

    def clean_password2(self):

        password1 = self.cleaned_data.get(
            "password1"
        )

        password2 = self.cleaned_data.get(
            "password2"
        )

        if (
            password1
            and password2
            and password1 != password2
        ):

            raise forms.ValidationError(
                "Las contraseñas no coinciden."
            )

        return password2

    def save(self, commit=True):

        user = super().save(
            commit=False
        )

        user.set_password(
            self.cleaned_data["password1"]
        )

        if commit:

            user.save()

        return user


# ======================================================
# REGISTRO DE USUARIO
# ======================================================

def register_view(request):

    form = RegisterForm()

    if request.method == "POST":

        form = RegisterForm(
            request.POST
        )

        if form.is_valid():

            user = form.save(
                commit=False
            )

            role = request.POST.get(
                "role"
            )

            # ==================================================
            # ASIGNACIÓN DE ROL
            # ==================================================

            if role in [
                "patient",
                "doctor"
            ]:

                user.role = role

            else:

                user.role = "patient"

            user.save()

            # ==================================================
            # AUDITORÍA - REGISTRO
            # ==================================================

            create_audit(

                user=user,

                action="create",

                module="users",

                object_id=user.id,

                description=(

                    f"El usuario {user.username} "

                    f"fue registrado en el sistema "

                    f"con rol {user.role}."

                ),

                request=request,

            )

            # ==================================================
            # INICIAR SESIÓN
            # ==================================================

            login(
                request,
                user
            )

            return redirect("/")

    return render(

        request,

        "users/register.html",

        {
            "form": form
        }

    )


# ======================================================
# LOGIN
# ======================================================

def login_view(request):

    username = ""

    error = None

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        )

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(

            request,

            username=username,

            password=password

        )

        if user is not None:

            login(
                request,
                user
            )

            # ==================================================
            # AUDITORÍA - LOGIN EXITOSO
            # ==================================================

            create_audit(

                user=user,

                action="login",

                module="users",

                object_id=user.id,

                description=(

                    f"El usuario {user.username} "

                    f"inició sesión en el sistema."

                ),

                request=request,

            )

            return redirect("/")

        # ==================================================
        # LOGIN FALLIDO
        # ==================================================

        error = (
            "Usuario o contraseña incorrectos."
        )

    return render(

        request,

        "users/login.html",

        {
            "username": username,
            "error": error,
        }

    )


# ======================================================
# LOGOUT
# ======================================================

def logout_view(request):

    user = request.user

    # ==================================================
    # AUDITORÍA - LOGOUT
    # ==================================================

    if user.is_authenticated:

        create_audit(

            user=user,

            action="logout",

            module="users",

            object_id=user.id,

            description=(

                f"El usuario {user.username} "

                f"cerró sesión."

            ),

            request=request,

        )

    logout(
        request
    )

    return redirect(
        "/users/login/"
    )


# ======================================================
# PERFIL DE USUARIO - API
# ======================================================

class ProfileAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    # ==================================================
    # CONSULTAR PERFIL
    # ==================================================

    def get(self, request):

        serializer = UserProfileSerializer(
            request.user
        )

        # ==================================================
        # AUDITORÍA - CONSULTAR PERFIL
        # ==================================================

        create_audit(

            user=request.user,

            action="read",

            module="users",

            object_id=request.user.id,

            description=(

                f"El usuario {request.user.username} "

                f"consultó su perfil."

            ),

            request=request,

        )

        return Response(

            serializer.data,

            status=status.HTTP_200_OK

        )

    # ==================================================
    # ACTUALIZAR PERFIL
    # ==================================================

    def put(self, request):

        serializer = UserProfileSerializer(

            request.user,

            data=request.data,

            partial=True

        )

        if serializer.is_valid():

            user = serializer.save()

            # ==================================================
            # AUDITORÍA - ACTUALIZAR PERFIL
            # ==================================================

            create_audit(

                user=request.user,

                action="update",

                module="users",

                object_id=user.id,

                description=(

                    f"El usuario {request.user.username} "

                    f"actualizó su perfil."

                ),

                request=request,

            )

            return Response(

                serializer.data,

                status=status.HTTP_200_OK

            )

        # ==================================================
        # DATOS INVÁLIDOS
        # ==================================================

        return Response(

            serializer.errors,

            status=status.HTTP_400_BAD_REQUEST

        )


# ======================================================
# LISTA DE PACIENTES - API
# ======================================================

@api_view(["GET"])
@permission_classes([
    IsAuthenticated
])
def patient_list_api(request):

    # ==================================================
    # VALIDACIÓN DE ROL
    # ==================================================
    #
    # Solamente administradores y doctores pueden
    # consultar la lista general de pacientes.
    #
    # Los pacientes autenticados no pueden consultar
    # información de otros pacientes.
    # ==================================================

    if request.user.role not in [
        "admin",
        "doctor"
    ]:

        # ==================================================
        # AUDITORÍA - ACCESO NO AUTORIZADO
        # ==================================================

        create_audit(

            user=request.user,

            action="denied",

            module="users",

            object_id=None,

            description=(

                f"El usuario {request.user.username} "

                f"con rol {request.user.role} "

                f"intentó consultar la lista de pacientes "

                f"sin permisos."

            ),

            request=request,

        )

        return Response(

            {
                "detail": (
                    "No tienes permisos para "
                    "consultar la lista de pacientes."
                )
            },

            status=status.HTTP_403_FORBIDDEN

        )

    # ==================================================
    # OBTENER PACIENTES
    # ==================================================

    patients = User.objects.filter(
        role="patient"
    )

    serializer = UserSerializer(
        patients,
        many=True
    )

    # ==================================================
    # AUDITORÍA - CONSULTA DE PACIENTES
    # ==================================================

    create_audit(

        user=request.user,

        action="read",

        module="users",

        object_id=None,

        description=(

            f"El usuario {request.user.username} "

            f"consultó la lista de pacientes."

        ),

        request=request,

    )

    return Response(

        serializer.data,

        status=status.HTTP_200_OK

    )

