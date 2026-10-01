from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    usuario = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get("request")
        identifier = attrs["usuario"].strip()
        password = attrs["password"]

        username = identifier
        if "@" in identifier:
            user_by_email = User.objects.filter(email__iexact=identifier).first()
            if user_by_email:
                username = user_by_email.get_username()

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Credenciales invalidas.")
        if not user.is_active:
            raise serializers.ValidationError("La cuenta esta inactiva.")

        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        validators=[validate_password],
    )
    password_confirmacion = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirmacion",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este email.")
        return email

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirmacion"):
            raise serializers.ValidationError({
                "password_confirmacion": "Las contraseñas no coinciden."
            })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class CurrentUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
        ]
        read_only_fields = ["id", "email", "is_staff"]
