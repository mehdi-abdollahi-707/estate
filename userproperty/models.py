from django.conf import settings
from django.db import models
from property.models import Property


class SaveProperty(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE , related_name='save_property')
    property = models.ForeignKey(Property , on_delete=models.CASCADE , related_name='save_property')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "property"],
                            name="unique_user_saved_property")]
