from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator


User = get_user_model()

business_phone_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="Enter a valid phone number. Format: 09xxxxxxxxx",
)


class Agency(models.Model):
    agent = models.OneToOneField(User , on_delete=models.CASCADE , related_name='agency')
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=155 , unique=True)
    business_phone = models.CharField(max_length=11 , validators=[business_phone_validator])
    description = models.TextField()
    province = models.CharField(max_length=122)
    city = models.CharField(max_length=122)
    exact_address = models.TextField()
    is_verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "agency"
        verbose_name_plural = "agencies"


class Inquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        CONTACTED = "CONTACTED", "Contacted"
        CLOSED = "CLOSED", "Closed"

    property = models.ForeignKey('property.Property' , on_delete=models.CASCADE , related_name='inquiries')
    customer = models.ForeignKey(User , on_delete=models.CASCADE , related_name='inquiries')
    message = models.TextField()
    status = models.CharField(max_length=10 , choices=Status.choices , default=Status.NEW)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry #{self.pk} - {self.property} - {self.customer}"

    class Meta:
        verbose_name = "inquiry"
        verbose_name_plural = "inquiries"
        ordering = ["-created"]
