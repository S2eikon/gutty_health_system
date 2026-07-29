from rest_framework import serializers

from django.conf import settings

from .models import MedicalDocument



class MedicalDocumentSerializer(serializers.ModelSerializer):


    patient_name = serializers.CharField(
        source="patient.get_full_name",
        read_only=True
    )


    uploaded_by_name = serializers.CharField(
        source="uploaded_by.get_full_name",
        read_only=True
    )


    document_type_display = serializers.CharField(
        source="get_document_type_display",
        read_only=True
    )


    file_url = serializers.SerializerMethodField(
        read_only=True
    )



    class Meta:

        model = MedicalDocument


        fields = [

            "id",

            "patient",
            "patient_name",

            "uploaded_by",
            "uploaded_by_name",

            "document_type",
            "document_type_display",

            "title",

            "description",

            "file",
            "file_url",

            "uploaded_at",
        ]


        read_only_fields = [

            "uploaded_at",
            "uploaded_by",
            "file_url",

        ]



    # ==================================================
    # VALIDAR ARCHIVO
    # ==================================================

    def validate_file(self, value):

        allowed_extensions = [

            "pdf",
            "jpg",
            "jpeg",
            "png",

        ]


        extension = value.name.split(".")[-1].lower()


        if extension not in allowed_extensions:

            raise serializers.ValidationError(
                "Solo se permiten archivos PDF, JPG, JPEG y PNG."
            )



        # Máximo 10 MB

        max_size = 10 * 1024 * 1024


        if value.size > max_size:

            raise serializers.ValidationError(
                "El archivo no puede superar los 10 MB."
            )


        return value



    # ==================================================
    # URL ARCHIVO
    # ==================================================

    def get_file_url(self, obj):

        request = self.context.get(
            "request"
        )


        if obj.file:

            if request:

                return request.build_absolute_uri(
                    obj.file.url
                )


            return obj.file.url


        return None