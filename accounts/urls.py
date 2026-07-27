from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path('user/register/send/code/' , views.SendOtpRegisterView.as_view(), name='register-send-code'),
    path('user/register/verify/code/' , views.VerifyOtpRegisterView.as_view(), name='register-verify-code'),
    path('user/complete/register/' , views.CompleteRegisterView.as_view(), name='complete-register'),
    path('user/login/send/code/' , views.SendOtpLoginView.as_view(), name='login-send-code'),
    path('user/login/verify/code/' , views.VerifyOtpLoginView.as_view(), name='login-verify-code'),
    path('user/info/' , views.UserSendInfoView.as_view(), name='user-info'),
    path('user/update/info/' , views.UserUpdateInfoView.as_view(), name='user-update-info'),
    path('user/reset/password/step1/' , views.UserResetPasswordStepOneView.as_view(), name='user-reset-password-step1'),
    path('user/reset/password/step2/' , views.UserResetPasswordStepTwoView.as_view(), name='user-reset-password-step2'),
    path('user/reset/password/step3/' , views.UserResetPasswordStepThreeView.as_view(), name='user-reset-password-step3'),
    path('user/change/phone/step1/' , views.SendOtpChangePhoneNumberView.as_view(), name='user-change-phone-step1'),
    path('user/change/phone/step2/' , views.VerifyOtpChangePhoneNumberView.as_view(), name='user-change-phone-step2'),
    path('user/delete/step1/' , views.UserDeleteAccountStep1View.as_view(), name='user-delete-account-one'),
    path('user/delete/step2/' , views.UserDeleteAccountStep2View.as_view(), name='user-delete-account-two'),
]