from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404


from rest_framework import status
from rest_framework.response import Response


from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes
)


from rest_framework.parsers import (
    MultiPartParser,
    FormParser
)


from users.permissions import (
    IsAdmin,
    IsAdminDoctorPatientReceptionist,
)


from users.models import User


from .models import MedicalDocument
from .serializers import MedicalDocumentSerializer





# ======================================================
# LISTAR DOCUMENTOS
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def documents_api(request):


    if request.user.role == "patient":

        documents = MedicalDocument.objects.filter(
            patient=request.user
        )

    else:

        documents = MedicalDocument.objects.all()



    serializer = MedicalDocumentSerializer(

        documents.order_by("-uploaded_at"),

        many=True,

        context={
            "request": request
        }

    )


    return Response(

        serializer.data,

        status=status.HTTP_200_OK

    )







# ======================================================
# CREAR DOCUMENTO
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
@parser_classes([
    MultiPartParser,
    FormParser
])
def create_document_api(request):


    print("\n" + "=" * 60)
    print("📤 CREANDO DOCUMENTO")
    print("USUARIO:", request.user.username)
    print("ROL:", request.user.role)
    print("DATA:", request.data)
    print("FILES:", request.FILES)
    print("=" * 60 + "\n")



    data = request.data.copy()



    # ==========================================
    # PACIENTE SUBE SU PROPIO DOCUMENTO
    # ==========================================

    if request.user.role == "patient":

        data["patient"] = request.user.id



    patient_id = data.get("patient")



    if not patient_id:

        return Response(

            {
                "error":
                "Debe seleccionar un paciente."
            },

            status=status.HTTP_400_BAD_REQUEST

        )



    patient = get_object_or_404(

        User,

        id=patient_id

    )



    print(
        "👤 PACIENTE:",
        patient.username,
        "| ROL:",
        patient.role
    )



    # ==========================================
    # VALIDAR PACIENTE
    # ==========================================

    if patient.role != "patient":

        return Response(

            {
                "error":
                f"El usuario {patient.username} no tiene rol paciente."
            },

            status=status.HTTP_400_BAD_REQUEST

        )



    # ==========================================
    # VALIDAR ARCHIVO
    # ==========================================

    if "file" not in request.FILES:


        return Response(

            {
                "error":
                "Debe adjuntar un archivo."
            },

            status=status.HTTP_400_BAD_REQUEST

        )



    # ==========================================
    # SERIALIZER
    # ==========================================

    serializer = MedicalDocumentSerializer(

        data=data,

        context={
            "request": request
        }

    )



    if serializer.is_valid():



        document = serializer.save(

            uploaded_by=request.user,

            patient=patient

        )



        print(
            "✅ DOCUMENTO CREADO ID:",
            document.id
        )



        response_serializer = MedicalDocumentSerializer(

            document,

            context={
                "request": request
            }

        )



        return Response(

            {

                "message":
                "Documento subido correctamente.",


                "document":
                response_serializer.data

            },

            status=status.HTTP_201_CREATED

        )



    print("\n" + "=" * 60)
    print("❌ ERROR SERIALIZER")
    print(serializer.errors)
    print("=" * 60 + "\n")



    return Response(

        {

            "message":
            "Error de validación.",


            "errors":
            serializer.errors

        },

        status=status.HTTP_400_BAD_REQUEST

    )







# ======================================================
# DESCARGAR DOCUMENTO
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def download_document_api(
    request,
    document_id
):


    if request.user.role == "patient":


        document = get_object_or_404(

            MedicalDocument,

            id=document_id,

            patient=request.user

        )


    else:


        document = get_object_or_404(

            MedicalDocument,

            id=document_id

        )



    if not document.file:

        raise Http404(
            "El documento no tiene archivo."
        )



    return FileResponse(

        document.file.open("rb"),

        as_attachment=True,

        filename=document.file.name.split("/")[-1]

    )







# ======================================================
# DETALLE DOCUMENTO
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def document_detail_api(
    request,
    document_id
):


    if request.user.role == "patient":

        document = get_object_or_404(

            MedicalDocument,

            id=document_id,

            patient=request.user

        )

    else:

        document = get_object_or_404(

            MedicalDocument,

            id=document_id

        )



    serializer = MedicalDocumentSerializer(

        document,

        context={
            "request": request
        }

    )



    return Response(

        serializer.data,

        status=status.HTTP_200_OK

    )







# ======================================================
# ELIMINAR DOCUMENTO
# ======================================================

@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_document_api(
    request,
    document_id
):


    document = get_object_or_404(

        MedicalDocument,

        id=document_id

    )



    if document.file:

        document.file.delete(

            save=False

        )



    document.delete()



    return Response(

        {

            "message":
            "Documento eliminado correctamente."

        },

        status=status.HTTP_200_OK

    )