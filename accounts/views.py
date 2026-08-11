from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (SendOtpSerializer, VerifyOtpSerializer,
                          CompleteRegistrationSerializer , UserSendInfoSerializer,
                          SendOtpLoginSerializer , UserUpdateInfoSerializer ,
                          UserResetPasswordSerializer)
from .otp import *
from .utils import send_otp_code
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from .services.otp_service import OTPService
from .services.auth_service import AuthService
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.contrib.auth import logout


User = get_user_model()




class SendOtpRegisterView(APIView):
    """
    Send Otp with phone_number and save code in redis
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = SendOtpSerializer

    def post(self , request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        # checking for repeated phone_number
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({'message':'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # check limit of sending otp in exact time
        if cache.get(otp_limit_key(phone_number)):
            return Response({"message" : "Try agin later"} , status=status.HTTP_429_TOO_MANY_REQUESTS)

        # send OTP
        try:
            session_token = OTPService.send_otp(phone_number)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"message" : "OTP code sent successfully" , "otp_session_token" : session_token}
            ,status=status.HTTP_200_OK)


class VerifyOtpRegisterView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = VerifyOtpSerializer

    def post(self , request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            phone_number = OTPService.verify_otp(
                serializer.validated_data['otp_session_token'],
                serializer.validated_data['otp_code'],
            )
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # generate token for complete registration
        new_session_token = generate_session_token()
        cache.set(otp_session_key(new_session_token), phone_number, timeout=600)

        return Response({
            "is_registered": False,
            "registration_token": new_session_token,
            "detail": "please complete your info"
        })


class CompleteRegisterView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = CompleteRegistrationSerializer

    def post(self , request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tokens = AuthService.complete_registration(serializer.data)
        except ValueError as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            tokens,
            status=status.HTTP_201_CREATED
        )


class SendOtpLoginView(APIView):
    """
    Send Otp with phone_number and save code in redis for login
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = SendOtpLoginSerializer

    def post(self , request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        # checking for existence of phone_number
        user = User.objects.filter(phone_number=phone_number).first()
        if not user or not user.check_password(password):
            return Response({'message':'Phone number not found or password is wrong'}, status=status.HTTP_400_BAD_REQUEST)

        # check limit of sending otp in exact time
        if cache.get(otp_limit_key(phone_number)):
            return Response({"message" : "Try agin later"} , status=status.HTTP_429_TOO_MANY_REQUESTS)

        # send OTP
        try:
            session_token = OTPService.send_otp(phone_number)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"message" : "OTP code sent successfully" , "otp_session_token" : session_token}
            ,status=status.HTTP_200_OK)


class VerifyOtpLoginView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = VerifyOtpSerializer

    def post(self , request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)

        try:
            phone_number = OTPService.verify_otp(
                serializer.validated_data['otp_session_token'],
                serializer.validated_data['otp_code'],
            )
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone_number=phone_number).first()

        refresh = RefreshToken.for_user(user)

        return Response({
            "access" : str(refresh.access_token),
            "refresh" : str(refresh)
        })


class UserSendInfoView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSendInfoSerializer

    def get(self , request):
        user = request.user
        serializer = self.serializer_class(instance=user)
        return Response(serializer.data , status=status.HTTP_200_OK)


class UserUpdateInfoView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateInfoSerializer

    def patch(self , request):
        user = request.user
        serializer = self.serializer_class(instance=user , data=request.data , partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data , status=status.HTTP_200_OK)


class UserResetPasswordStepOneView(APIView):
    """
    Reset password step one : send otp code
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SendOtpSerializer
    def post(self , request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        if not User.objects.filter(phone_number=phone_number).exists():
            return Response({"message" : "phone number is wrong"} , status=status.HTTP_400_BAD_REQUEST)

        if cache.get(otp_limit_key(phone_number)):
            return Response({"message" : "Try agin later"} , status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            session_token = OTPService.send_otp(phone_number)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message" : "OTP code sent successfully" , "otp_session_token" : session_token }
                         , status=status.HTTP_200_OK)


class UserResetPasswordStepTwoView(APIView):
    """
    Reset password step two : verify otp code
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = VerifyOtpSerializer

    def post(self , request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)

        try:
            phone_number = OTPService.verify_otp(
                serializer.validated_data['otp_session_token'],
                serializer.validated_data['otp_code'],
            )
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

        new_session_token = generate_session_token()
        cache.set(otp_session_key(new_session_token), phone_number , timeout=3600)

        return Response({"message" : "Otp accepted successfully" ,
                         "reset_token" : new_session_token } , status=status.HTTP_200_OK)


class UserResetPasswordStepThreeView(APIView):
    """
    Reset password step three : Changing password
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UserResetPasswordSerializer

    def post(self , request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)

        try:
            AuthService.reset_password(serializer.validated_data)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message" : "Password reset successful" ,} , status=status.HTTP_200_OK)


class SendOtpChangePhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SendOtpSerializer

    def post(self , request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        if User.objects.filter(phone_number=phone_number).exists():
            return Response({"message" : "Try another phone number"} , status=status.HTTP_400_BAD_REQUEST)

        if cache.get(otp_limit_key(phone_number)):
            return Response({"message" : "Try agin later"} , status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            session_token = OTPService.send_otp(phone_number)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message" : "OTP code sent successfully" , "otp_session_token" : session_token }
                        , status=status.HTTP_200_OK)


class VerifyOtpChangePhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyOtpSerializer

    def post(self , request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)

        try:
            phone_number = OTPService.verify_otp(
                serializer.validated_data['otp_session_token'],
                serializer.validated_data['otp_code'],
            )
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=phone_number).exists():
            return Response({"message" : "Try another phone number"} , status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.phone_number = phone_number
        user.save()
        return Response({"message" : "Phone number changed successfully" ,} , status=status.HTTP_200_OK)



class UserDeleteAccountStep1View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self , request):
        phone_number = request.user.phone_number

        if cache.get(otp_limit_key(phone_number)):
            return Response({"message" : "Try agin later"} , status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            session_token = OTPService.send_otp(phone_number)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message" : "otp send to you" , "otp_session_token" : session_token} , status=status.HTTP_200_OK)


class UserDeleteAccountStep2View(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyOtpSerializer

    def post(self , request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)

        try:
            phone_number = OTPService.verify_otp(
                serializer.validated_data['otp_session_token'],
                serializer.validated_data['otp_code'],
            )

            if phone_number != request.user.phone_number:
                return Response({"message": "You are not the owner"}, status=status.HTTP_400_BAD_REQUEST)

            request.user.delete()
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)














