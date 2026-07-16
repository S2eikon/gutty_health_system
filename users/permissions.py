from rest_framework.permissions import BasePermission

# ======================================================
# PERMISOS INDIVIDUALES
# ======================================================

class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "admin"
        )


class IsDoctor(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "doctor"
        )


class IsPatient(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "patient"
        )


class IsReceptionist(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "receptionist"
        )


# ======================================================
# PERMISOS COMBINADOS
# ======================================================

class IsAdminOrDoctor(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["admin", "doctor"]
        )


class IsAdminOrReceptionist(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["admin", "receptionist"]
        )


class IsAdminOrPatient(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["admin", "patient"]
        )


# ======================================================
# NUEVO PERMISO PARA ADMIN, DOCTOR, PACIENTE Y RECEPCIONISTA
# ======================================================

class IsAdminDoctorPatientReceptionist(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in [
                "admin",
                "doctor",
                "patient",
                "receptionist"
            ]
        )
