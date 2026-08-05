from rest_framework.decorators import (
    api_view,
    permission_classes
)

from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from rest_framework import status

from .models import MedicalRecord

from .serializers import MedicalRecordSerializer

from audit.services import create_audit


# =====================================================
# LISTAR HISTORIALES MÉDICOS
# =====================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medical_record_list(request):

    records = MedicalRecord.objects.all().order_by(
        '-created_at'
    )

    serializer = MedicalRecordSerializer(
        records,
        many=True
    )

    # =================================================
    # AUDITORÍA - CONSULTAR HISTORIALES
    # =================================================

    create_audit(

        user=request.user,

        action="read",

        module="medical_records",

        object_id=None,

        description=(
            f"El usuario {request.user.username} "
            f"consultó la lista de historiales médicos."
        ),

        request=request

    )

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(

        serializer.data,

        status=status.HTTP_200_OK

    )


# =====================================================
# CREAR HISTORIAL MÉDICO
# =====================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_medical_record(request):

    serializer = MedicalRecordSerializer(
        data=request.data
    )

    # =================================================
    # VALIDAR INFORMACIÓN
    # =================================================

    if serializer.is_valid():

        # =============================================
        # GUARDAR HISTORIAL
        # =============================================

        record = serializer.save()

        # =============================================
        # AUDITORÍA - CREAR HISTORIAL
        # =============================================

        create_audit(

            user=request.user,

            action="create",

            module="medical_records",

            object_id=record.id,

            description=(
                f"El usuario {request.user.username} "
                f"creó el historial médico con ID "
                f"{record.id}."
            ),

            request=request

        )

        # =============================================
        # RESPUESTA
        # =============================================

        return Response(

            serializer.data,

            status=status.HTTP_201_CREATED

        )

    # =================================================
    # ERROR DE VALIDACIÓN
    # =================================================

    return Response(

        serializer.errors,

        status=status.HTTP_400_BAD_REQUEST

    )


# =====================================================
# ACTUALIZAR HISTORIAL MÉDICO
# =====================================================

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_medical_record(request, pk):

    # =================================================
    # BUSCAR HISTORIAL
    # =================================================

    try:

        record = MedicalRecord.objects.get(
            pk=pk
        )

    except MedicalRecord.DoesNotExist:

        return Response(

            {
                'error':
                'Historial no encontrado'
            },

            status=status.HTTP_404_NOT_FOUND

        )

    # =================================================
    # ACTUALIZAR
    # =================================================

    serializer = MedicalRecordSerializer(

        record,

        data=request.data,

        partial=True

    )

    # =================================================
    # VALIDAR
    # =================================================

    if serializer.is_valid():

        record = serializer.save()

        # =============================================
        # AUDITORÍA - ACTUALIZAR HISTORIAL
        # =============================================

        create_audit(

            user=request.user,

            action="update",

            module="medical_records",

            object_id=record.id,

            description=(
                f"El usuario {request.user.username} "
                f"actualizó el historial médico "
                f"con ID {record.id}."
            ),

            request=request

        )

        # =============================================
        # RESPUESTA
        # =============================================

        return Response(

            serializer.data,

            status=status.HTTP_200_OK

        )

    # =================================================
    # ERROR DE VALIDACIÓN
    # =================================================

    return Response(

        serializer.errors,

        status=status.HTTP_400_BAD_REQUEST

    )


# =====================================================
# ELIMINAR HISTORIAL MÉDICO
# =====================================================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_medical_record(request, pk):

    # =================================================
    # BUSCAR HISTORIAL
    # =================================================

    try:

        record = MedicalRecord.objects.get(
            pk=pk
        )

    except MedicalRecord.DoesNotExist:

        return Response(

            {
                'error':
                'Historial no encontrado'
            },

            status=status.HTTP_404_NOT_FOUND

        )

    # =================================================
    # GUARDAR ID ANTES DE ELIMINAR
    # =================================================

    record_id = record.id

    # =================================================
    # ELIMINAR HISTORIAL
    # =================================================

    record.delete()

    # =================================================
    # AUDITORÍA - ELIMINAR HISTORIAL
    # =================================================

    create_audit(

        user=request.user,

        action="delete",

        module="medical_records",

        object_id=record_id,

        description=(
            f"El usuario {request.user.username} "
            f"eliminó el historial médico "
            f"con ID {record_id}."
        ),

        request=request

    )

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(

        {
            'message':
            'Historial eliminado correctamente'
        },

        status=status.HTTP_200_OK

    )