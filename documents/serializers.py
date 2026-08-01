from rest_framework import serializers

from .models import MedicalDocument



class MedicalDocumentSerializer(serializers.ModelSerializer):


    # ==========================================
    # CAMPOS PERSONALIZADOS
    # ==========================================

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

            "title",

            "document_type",
            "document_type_display",

            "description",

            "file",
            "file_url",

            "uploaded_at",

        ]


        read_only_fields = [

            "id",

            "uploaded_by",

            "uploaded_by_name",

            "patient_name",

            "document_type_display",

            "uploaded_at",

            "file_url",

        ]


        extra_kwargs = {

            "description": {
                "required": False,
                "allow_blank": True
            },

            "file": {
                "required": True
            }

        }




    # ==========================================
    # VALIDAR TITULO
    # ==========================================

    def validate_title(self, value):

        value = value.strip()


        if not value:

            raise serializers.ValidationError(
                "El título del documento es obligatorio."
            )


        return value




    # ==========================================
    # VALIDAR DESCRIPCIÓN
    # ==========================================

    def validate_description(self, value):


        if value and len(value) > 500:

            raise serializers.ValidationError(
                "La descripción no puede superar los 500 caracteres."
            )


        return value




    # ==========================================
    # VALIDAR TIPO DOCUMENTO
    # ==========================================

    def validate_document_type(self, value):


        allowed = [

            "exam",
            "photo",
            "image",
            "prescription",
            "consent",
            "order",
            "other"

        ]


        if value not in allowed:

            raise serializers.ValidationError(
                "Tipo de documento inválido."
            )


        return value




    # ==========================================
    # VALIDAR ARCHIVO
    # ==========================================

    def validate_file(self, value):


        allowed_extensions = [

            "pdf",
            "jpg",
            "jpeg",
            "png"

        ]


        extension = (
            value.name
            .split(".")[-1]
            .lower()
        )


        if extension not in allowed_extensions:

            raise serializers.ValidationError(
                "Solo se permiten archivos PDF, JPG, JPEG y PNG."
            )



        max_size = 10 * 1024 * 1024


        if value.size > max_size:

            raise serializers.ValidationError(
                "El archivo no puede superar los 10 MB."
            )


        return value




    # ==========================================
    # URL ARCHIVO
    # ==========================================

    def get_file_url(self, obj):


        if not obj.file:

            return None



        request = self.context.get(
            "request"
        )


        if request:

            return request.build_absolute_uri(
                obj.file.url
            )


        return obj.file.url