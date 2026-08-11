import uuid
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction, IntegrityError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from agencies.models import Agency
from django.utils.text import slugify
from .validators import validate_image_size


class Property(models.Model):
    class Meta:
        ordering = ["-created"]
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    class ListingType(models.TextChoices):
        SALE = "SALE", "For Sale"
        RENT = "RENT", "For Rent"

    class PropertyType(models.TextChoices):
        APARTMENT = "APARTMENT", "Apartment"
        HOUSE = "HOUSE", "House"
        VILLA = "VILLA", "Villa"
        LAND = "LAND", "Land"
        OFFICE = "OFFICE", "Office"
        SHOP = "SHOP", "Shop"
        WAREHOUSE = "WAREHOUSE", "Warehouse"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        SOLD = "SOLD", "Sold"
        RENTED = "RENTED", "Rented"
        PENDING = "PENDING", "Pending"

    agency = models.ForeignKey(Agency,on_delete=models.CASCADE ,related_name="properties")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,blank=True,max_length=280,allow_unicode=True)
    description = models.TextField()
    listing_type = models.CharField(max_length=10,choices=ListingType.choices , db_index=True)
    property_type = models.CharField(max_length=20,choices=PropertyType.choices , db_index=True)
    status = models.CharField(max_length=10,choices=Status.choices,default=Status.ACTIVE , db_index=True)
    price = models.PositiveBigIntegerField(db_index=True)
    area = models.PositiveIntegerField(help_text="Square meters")
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    has_parking = models.BooleanField(default=False)
    floor = models.PositiveSmallIntegerField(null=True,blank=True)
    total_floors = models.PositiveSmallIntegerField(null=True,blank=True)
    year_built = models.PositiveIntegerField(null=True,blank=True,validators=[MaxValueValidator(9999)])
    province = models.CharField(max_length=100 , db_index=True)
    city = models.CharField(max_length=100 , db_index=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True,
                                    validators=[MinValueValidator(-90),MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True,
                                     validators=[MinValueValidator(-180),MaxValueValidator(180)])
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True , db_index=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.slug:
            super().save(*args, **kwargs)
            return

        base_slug = slugify(f"{self.title}-{self.city}", allow_unicode=True) or uuid.uuid4().hex[:10]
        slug = base_slug
        counter = 1
        for _ in range(20):
            self.slug = slug
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                return
            except IntegrityError:
                counter += 1
                slug = f"{base_slug}-{counter}"

        raise IntegrityError("Could not generate a unique slug for Property")



class PropertyImage(models.Model):

    property = models.ForeignKey(Property,related_name="images",on_delete=models.CASCADE)
    image = models.ImageField(upload_to="properties/",validators=[validate_image_size])
    is_first = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


@receiver(post_delete, sender=PropertyImage)
def delete_property_image_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
