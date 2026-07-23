from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

from .models import Bill
from .serializers import BillSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_list(request):
    bills = Bill.objects.all().order_by('-created_at')
    serializer = BillSerializer(bills, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bill_create(request):
    serializer = BillSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def bill_update(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    serializer = BillSerializer(bill, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bill_delete(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    bill.delete()
    return Response({"message": "Factura eliminada"})
