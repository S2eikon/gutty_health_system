from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import MedicalRecord
from .serializers import MedicalRecordSerializer


# ==========================================
# LISTAR HISTORIALES
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medical_record_list(request):

    records = MedicalRecord.objects.all().order_by('-created_at')

    serializer = MedicalRecordSerializer(
        records,
        many=True
    )

    return Response(serializer.data)


# ==========================================
# CREAR HISTORIAL
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_medical_record(request):

    serializer = MedicalRecordSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ==========================================
# ACTUALIZAR HISTORIAL
# ==========================================

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_medical_record(request, pk):

    try:

        record = MedicalRecord.objects.get(pk=pk)

    except MedicalRecord.DoesNotExist:

        return Response(
            {'error': 'Historial no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = MedicalRecordSerializer(
        record,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():

        serializer.save()

        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ==========================================
# ELIMINAR HISTORIAL
# ==========================================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_medical_record(request, pk):

    try:

        record = MedicalRecord.objects.get(pk=pk)

    except MedicalRecord.DoesNotExist:

        return Response(
            {'error': 'Historial no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    record.delete()

    return Response(
        {'message': 'Historial eliminado correctamente'},
        status=status.HTTP_200_OK
    )