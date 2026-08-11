from django.contrib.auth import get_user_model
from rest_framework import serializers
import re
from django.contrib.auth.password_validation import validate_password

User = get_user_model()



class SendOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11 ,required=True)

    def validate_phone_number(self, value):
        value = value.strip()

        if re.fullmatch(r"9\d{9}", value):  # اگر کاربر 912 فرستاد
            value = "0" + value

        if not re.fullmatch(r"09\d{9}", value):
            raise serializers.ValidationError("شماره موبایل معتبر نیست. باید با 09 شروع شود.")

        return value

class SendOtpLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11 ,required=True)
    password = serializers.CharField()

    def validate_phone_number(self, value):
        value = value.strip()

        if re.fullmatch(r"9\d{9}", value):  # اگر کاربر 912 فرستاد
            value = "0" + value

        if not re.fullmatch(r"09\d{9}", value):
            raise serializers.ValidationError("شماره موبایل معتبر نیست. باید با 09 شروع شود.")

        return value



class VerifyOtpSerializer(serializers.Serializer):
    otp_session_token = serializers.CharField()
    otp_code = serializers.CharField(max_length=5)


class CompleteRegistrationSerializer(serializers.Serializer):
    registration_token = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[
        (User.Role.AGENT , 'Agent'),
        (User.Role.CUSTOMER , 'Customer'),
    ])
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self , data):
        pass1 = data['password']
        pass2 = data['confirm_password']
        if pass1 != pass2:
            raise serializers.ValidationError("Passwords don't match.")
        return data

class UserSendInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'first_name', 'last_name', 'role')



class UserUpdateInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',)

    def validate_email(self, value):
        if User.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class UserResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self , data):
        pass1 = data['password']
        pass2 = data['confirm_password']
        if pass1 != pass2:
            raise serializers.ValidationError("Passwords don't match.")
        return data
