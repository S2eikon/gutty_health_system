from .models import AuditLog



# =====================================================
# SERVICIO GENERAL DE AUDITORÍA
# =====================================================

def create_audit(

    user,

    action,

    module,

    description,

    object_id=None,

    request=None

):


    # ==============================================
    # OBTENER IP DEL USUARIO
    # ==============================================

    ip_address = None


    if request:

        ip_address = request.META.get(
            "REMOTE_ADDR"
        )


    # ==============================================
    # CREAR REGISTRO DE AUDITORÍA
    # ==============================================

    audit_log = AuditLog.objects.create(

        user=user,

        action=action,

        module=module,

        object_id=object_id,

        description=description,

        ip_address=ip_address

    )


    return audit_log