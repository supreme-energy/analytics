from django.db import models
from django.contrib.auth.models import User
from phone_field import PhoneField


class Person(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    type = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    level = models.CharField(max_length=50, default="0")
    department = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50)  # autofill
    phone = PhoneField(blank=True, help_text="Contact Phone Number")
    e_contact_first_name = models.CharField(max_length=50)
    e_contact_last_name = models.CharField(max_length=50)
    e_contact_cell_phone = PhoneField(help_text="Contact Phone Number")
    e_contact_work_phone = PhoneField(
        help_text="Contact Phone Number")  # default=e_contact_cell_phone
    e_contact_relationship = models.CharField(max_length=50)

    def __str__(self):
        return 'First Name: %s, Last Name: %s' % (self.first_name, self.last_name)

    class Meta:
        verbose_name_plural = "Personnel"
