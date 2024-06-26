from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

from account.managers import UserManager


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return f"{self.pk} {self.email}"

    @property
    def has_profile(self) -> bool:
        try:
            self.profile
        except self.__class__.profile.RelatedObjectDoesNotExist:
            return False

        return True
