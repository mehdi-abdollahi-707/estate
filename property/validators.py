from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE_MB = 5


def validate_image_size(image):
    max_size = MAX_IMAGE_SIZE_MB * 1024 * 1024
    if image.size > max_size:
        raise ValidationError(f"Image size should not exceed {MAX_IMAGE_SIZE_MB}MB.")
