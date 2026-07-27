from django.core.cache import cache
from accounts.otp import *
from accounts.utils import send_otp_code
from django.contrib.auth import get_user_model



User = get_user_model()
MAX_OTP_ATTEMPTS = 10

class OTPService:

    @staticmethod
    def send_otp(phone_number):
        code = generate_otp_code()
        session_token = generate_session_token()

        send_otp_code(phone_number , code)

        cache.set(otp_data_key(phone_number), code, timeout=OTP_TTL_SECONDS)

        cache.set(otp_limit_key(phone_number) , True , timeout=OTP_RATE_LIMIT_SECONDS)

        cache.set(otp_session_key(session_token) , phone_number , timeout=OTP_TTL_SECONDS)

        cache.delete(f"otp attempts for {phone_number}")

        return session_token

    @staticmethod
    def verify_otp(session_token , user_code):
        phone_number = cache.get(otp_session_key(session_token))

        if not phone_number:
            raise ValueError("Token expired")

        attempts_key = f"otp attempts for {phone_number}"
        attempts = cache.get(attempts_key , 0)

        if attempts >= MAX_OTP_ATTEMPTS:
            cache.delete(otp_data_key(phone_number))
            cache.delete(otp_session_key(session_token))
            cache.delete(attempts_key)

            raise ValueError("Too many otp attempts")

        stored_code = cache.get(otp_data_key(phone_number))
        if not stored_code:
            raise ValueError("Otp Expired")

        if stored_code != user_code:
            cache.set(attempts_key , attempts +1 , timeout=OTP_TTL_SECONDS)
            raise ValueError("Invalid OTP")

        cache.delete(otp_data_key(phone_number))
        cache.delete(otp_session_key(session_token))
        cache.delete(attempts_key)


        return phone_number