from django.contrib.auth import authenticate, get_user_model
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
